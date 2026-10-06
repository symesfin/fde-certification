# A plain, readable Dockerfile. Not the smallest possible image, not the
# cleverest. You should be able to read every line and say what it does.

FROM python:3.12-slim

# uv installs dependencies fast and is already how we run things locally.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy the dependency manifests first. Docker caches layers, so dependencies
# only reinstall when these change -- not on every code edit.
COPY pyproject.toml uv.lock ./

# Install from the LOCK, not from pyproject.toml. pyproject says "gradio>=6.0",
# which resolves to whatever is newest on the day you build -- so an image built
# today and one built next month are different applications wearing the same
# tag. The lock pins every package, including the ones you never asked for.
RUN uv export --frozen --no-dev --no-emit-project -o requirements.txt \
 && uv pip install --system --no-cache -r requirements.txt

COPY llm.py app.py ./
COPY frontend/ ./frontend/

# Don't run as root. Your security review will ask about this.
RUN useradd --create-home appuser
USER appuser

EXPOSE 7860

# The API key is NOT baked into this image. It arrives at runtime via
# environment variable. Never COPY a .env file into a container image --
# anyone who can pull the image can read it.
CMD ["python", "app.py"]
