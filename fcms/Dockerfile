FROM python:3.10-slim 

ARG USERNAME=appuser
ARG APPDIR=/app

# These env variables should be provided in deployment
ENV MONGODB_URI=
ENV GOOGLE_APPLICATION_CREDENTIALS=${APPDIR}/google_cred.json
ENV GOOGLE_CLOUD_BUCKET=

# i4u settings
ENV I4U_USER=
ENV I4U_PASS=

# SMTP settings
ENV SMTP_USER=
ENV SMTP_PASS=
ENV SMTP_HOST=
ENV SMTP_PORT=

# Set this to a test email address to ensure no real emails will be sent out
ENV SMTP_TEST=

WORKDIR ${APPDIR}
COPY . ${APPDIR}

RUN useradd --no-create-home --home-dir=${APPDIR} ${USERNAME} \
  && chown -R ${USERNAME}:${USERNAME} ${APPDIR}

RUN python -m pip install --upgrade --no-cache-dir pip \
  && pip install --upgrade --no-cache-dir -r ${APPDIR}/requirements.txt

ENV PYTHONPATH=${APPDIR}

USER ${USERNAME}
VOLUME [ "${GOOGLE_APPLICATION_CREDENTIALS}" ]
EXPOSE 8000
CMD [ "uvicorn", "main:app", "--host=0.0.0.0" ]
