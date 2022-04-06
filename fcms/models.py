import logging

from pydantic import BaseModel, Field

logger = logging.getLogger("fcms")


class CaseSearch(BaseModel):
    text: str | None = None
    ended: bool | None = None
    case_type: str | None = None
    pipeline: list[dict] = Field(default_factory=list)

    def do_search(self):
        bool_pipelines = {
            "ended": [
                {
                    "$lookup": {
                        "from": "stages",
                        "localField": "current_stage",
                        "foreignField": "_id",
                        "as": "extras.current_stage",
                    }
                },
                {"$unwind": {"path": "$extras.current_stage"}},
                {"$match": {"extras.current_stage.is_last": self.ended}},
            ],
            "debt": [],
        }

        for field, value in self.dict(exclude_none=True, skip_defaults=True).items():
            print(field, value)
            if field == "text":
                self.prepare_free_search_pipeline()
            elif isinstance(value, str) and value:
                self.pipeline += [{"$match": {field: value}}]
            elif isinstance(value, bool):
                self.pipeline += bool_pipelines[field]

    def prepare_free_search_pipeline(self):
        raise NotImplementedError  # TODO
