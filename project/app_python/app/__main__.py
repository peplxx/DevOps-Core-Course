import os
from pathlib import Path
import uvicorn
from app.settings import settings

# Change dir to project root (one level up from this file)
os.chdir(Path(__file__).parents[1])

if __name__ == "__main__":
    uvicorn.run(
        "app.app:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        use_colors=True,
        proxy_headers=True,
        forwarded_allow_ips="*",
    )