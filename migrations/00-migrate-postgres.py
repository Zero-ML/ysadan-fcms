import os
import psycopg2
import dotenv
import pymongo

from datetime import datetime, date
from psycopg2.extras import RealDictCursor, RealDictRow

if __name__ == "__main__":
    dotenv.load_dotenv()
    allowed = "fcms-dev"
    db = pymongo.MongoClient(os.getenv("MONGODB_URI")).get_default_database()
    if db.name != allowed:
        raise PermissionError(
            f"This function must only run on {allowed}, not {db.name}"
        )
    postgres = psycopg2.connect(
        os.getenv("POSTGRES_URI"), cursor_factory=RealDictCursor
    )
    cursor = postgres.cursor()
    cursor.execute(
        "SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = 'public'"
    )
    old_tables = [item["tablename"] for item in cursor.fetchall()]  # type: list[str]

    # Main import stage
    for table in old_tables:
        print(f"Importing {table}")
        db.drop_collection(table)
        cursor = postgres.cursor()
        cursor.execute(f"SELECT * FROM {table}")
        data = cursor.fetchall()  # type: list[RealDictRow]  # Not really a list

        if table.endswith("_list"):
            if table.startswith("status"):
                stages = [
                    {"name": stage, "is_last": stage in ["נסגר", "בוטל"]}
                    for stage in [row["status"] for row in data]
                ]
                db.drop_collection("stages")
                db["stages"].insert_many(stages)
            elif table.startswith("cities"):
                pass
            else:
                print(
                    f"WARNING: Skipping {table}"
                )  # Do not handle other static lists yet, see if different method works
        else:
            for i, row in enumerate(data):
                for key, value in row.items():
                    if isinstance(value, date):
                        data[i][key] = datetime.combine(value, datetime.min.time())
            if data:
                if table == "actions":  # To change actions into case_logs
                    table = "case_logs"
                    db.drop_collection(table)
                db[table].insert_many(data)
                db[table].update_many(
                    {}, {"$unset": {"id": "", "action_key": "", "bill_key": ""}}
                )  # Remove old irrelevant indexes
    print("Done importing from postgres")

    # Fix data stage
    print("Referencing contacts in cases")
    case_contacts = db["cases"].aggregate(
        [
            {
                "$lookup": {
                    "from": "case_contacts",
                    "localField": "case_key",
                    "foreignField": "case_key",
                    "as": "case_contacts",
                }
            },
            {
                "$lookup": {
                    "from": "contacts",
                    "localField": "case_contacts.contact_key",
                    "foreignField": "contact_key",
                    "as": "contacts",
                }
            },
            {"$project": {"case_contacts": 0}},
            {"$set": {"contacts": "$contacts._id"}},
            {"$out": "cases"},
        ]
    )
    db.drop_collection("case_contacts")

    print("Fixing case_logs field names")
    db["case_logs"].aggregate(
        [
            {"$set": {"date": "$action_date"}},
            {"$project": {"action_date": 0}},
            {"$out": "case_logs"},
        ]
    )

    print("Referencing current_stage and removing old status field")
    db["cases"].aggregate(
        [
            {
                "$lookup": {
                    "from": "stages",
                    "localField": "status",
                    "foreignField": "name",
                    "as": "current_stage",
                }
            },
            {"$unwind": {"path": "$current_stage", "preserveNullAndEmptyArrays": True}},
            {"$project": {"status": 0}},
            {"$set": {"current_stage": "$current_stage._id"}},
            {"$out": "cases"},
        ]
    )
