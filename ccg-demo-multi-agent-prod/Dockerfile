# Multi-Agent Timesheet Assistant - PRODUCTION VERSION
FROM python:3.13-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY agents/ ./agents/
COPY tools/ ./tools/
COPY shared/ ./shared/
COPY multi_agent_streamlit.py .
COPY .env.example .env

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run Streamlit
CMD ["streamlit", "run", "multi_agent_streamlit.py", "--server.port=8501", "--server.address=0.0.0.0"]
