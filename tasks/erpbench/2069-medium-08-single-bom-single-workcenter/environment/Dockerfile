# Materialized fully by the Stage-6 Harbor exporter, which bakes into the image:
#   /app/run/world.sqlite   (core + this task's seed layers, via sim/prepare.py)
#   /app/mcp/, /app/verifiers/, /app/sim/   (servers, verifier engine, oracle)
# Local calibration runs use sim/run_task.py directly and do not need Docker.
FROM python:3.12-slim
WORKDIR /app
COPY . /app/task
CMD ["sleep", "infinity"]
