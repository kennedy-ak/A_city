"""
Development server startup script
"""

import uvicorn
import os
from pathlib import Path

# Load environment variables if .env exists
env_file = Path(__file__).parent / '.env'
if env_file.exists():
    from dotenv import load_dotenv
    load_dotenv(env_file)

if __name__ == "__main__":
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    print(f"""
    🚀 Starting Afrimash Customer Intelligence API
    📍 Server: http://{host}:{port}
    📚 Docs: http://localhost:{port}/docs
    🔧 Debug Mode: {debug}
    """)
    
    uvicorn.run(
        "app.api.main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )

