# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /skw

# Create a non‑root user
RUN useradd -m -u 1000 user
USER user

# Add user's local bin to PATH
ENV PATH="/home/user/.local/bin:$PATH"

# Copy requirements first (for better caching)
COPY --chown=user requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY --chown=user . .

# Expose Streamlit’s default port
EXPOSE 7860

# Start Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]