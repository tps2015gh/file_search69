import sys
import json
import subprocess

def handle_request(req):
    """ Handle incoming JSON-RPC requests from an MCP client """
    if req.get("method") == "find_structural_neighbors":
        params = req.get("params", {})
        target_path = params.get("target_path")
        limit = params.get("limit", 5)
        
        if not target_path:
            return {"error": {"code": -32602, "message": "Missing target_path parameter"}}
            
        # ARCHITECTURE NOTE: 
        # We spawn ai_skill.py as a subprocess instead of importing it.
        # This guarantees that the heavy NumPy calculations and database reads 
        # occur in a completely isolated process that releases all memory instantly upon exit.
        # This prevents the long-running MCP Server from suffering memory leaks or hogging PC resources.
        try:
            result = subprocess.check_output(["python", "ai_skill.py", target_path, "--limit", str(limit)], text=True)
            # Parse the JSON string outputted by ai_skill.py and embed it in the RPC response
            return {"result": json.loads(result)}
        except subprocess.CalledProcessError as e:
            return {"error": {"code": -32603, "message": f"Execution failed: {e.output}"}}
        except Exception as e:
            return {"error": {"code": -32603, "message": str(e)}}
            
    return {"error": {"code": -32601, "message": "Method not found"}}

def main():
    # Simple JSON-RPC loop over standard input/output
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            res = handle_request(req)
            if "id" in req:
                res["id"] = req["id"]
            res["jsonrpc"] = "2.0"
            print(json.dumps(res))
            sys.stdout.flush()
        except Exception as e:
            err = {"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}}
            print(json.dumps(err))
            sys.stdout.flush()

if __name__ == "__main__":
    main()
