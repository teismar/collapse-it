FROM ubuntu:latest
LABEL authors="teismar"

ENTRYPOINT ["top", "-b"]