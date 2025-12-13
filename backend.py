import modal
import json
from datetime import datetime

app = modal.App("concept-learning-backend")


volume = modal.Volume.from_name("experiment_responses", create_if_missing=True)

@app.function(volumes={"/data": volume})
@modal.fastapi_endpoint(method="POST", docs=True)
def submit(request: dict):
    """
    """
   
    try:
        data = request
    except Exception as e:
        return {"status": "error", "message": f"Invalid JSON body: {str(e)}"}

    # Timestamped filename
    timestamp = datetime.utcnow().isoformat().replace(":", "-")
    filename = f"/data/{timestamp}.json"

    # Write JSON file to the volume
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

    volume.commit()

    return {"status": "ok", "saved_as": filename}