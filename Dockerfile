# Multi-Stage-Build: kleines, sicheres Endimage.
#
# Stage 1 ("builder") installiert Abhängigkeiten in ein virtuelles Env.
# Stage 2 ("runtime") kopiert nur das Nötige -> schlankes Image ohne Build-Tools.

# ---------- Stage 1: Build ----------
FROM python:3.12-slim AS builder

WORKDIR /app

# Nur die Requirements zuerst kopieren -> nutzt den Docker-Layer-Cache,
# solange sich die Abhängigkeiten nicht ändern.
COPY requirements.txt .
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# ---------- Stage 2: Runtime ----------
FROM python:3.12-slim AS runtime

# Nicht als root laufen (Sicherheit).
RUN useradd --create-home --uid 1000 appuser
WORKDIR /app

# Virtuelle Umgebung aus dem Builder übernehmen.
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Anwendungscode kopieren.
COPY app ./app

USER appuser
EXPOSE 8000

# Health-Check: Docker/Orchestrierer können so den Zustand prüfen.
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
