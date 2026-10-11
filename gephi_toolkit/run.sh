#!/usr/bin/env bash
# Builds and runs GephiPipeline.java with the official Gephi Toolkit 0.10.1.
# Requires Java 11+ (tested with OpenJDK 21). Downloads the toolkit jar (~83 MB) once.
set -euo pipefail
cd "$(dirname "$0")"

JAR=gephi-toolkit-0.10.1-all.jar
if [ ! -f "$JAR" ]; then
  curl -fL -o "$JAR" https://github.com/gephi/gephi-toolkit/releases/download/v0.10.1/gephi-toolkit-0.10.1-all.jar
fi

mkdir -p build
javac -cp "$JAR" -d build GephiPipeline.java
# PNG export needs a display; on a server without one, run under xvfb-run
if [ -z "${DISPLAY:-}" ] && command -v xvfb-run >/dev/null; then RUN="xvfb-run -a"; else RUN=""; fi
$RUN java --add-opens java.base/java.net=ALL-UNNAMED --add-opens java.base/java.lang=ALL-UNNAMED --add-opens java.base/java.util=ALL-UNNAMED -Dnetbeans.user=build/nbuser -cp "$JAR:build" GephiPipeline ..
