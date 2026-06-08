#!/usr/bin/env python3
"""钉钉文档 MCP 网关调用工具 - 直接通过 HTTP 调用"""
import json, sys, os, urllib.request, urllib.error

MCP_URL = "https://mcp-gw.dingtalk.com/server/b118049698978765178a66f3088450db5f55827f17eb3f44000a1b21e262b002?key=44b1dc761150599c39d83e79814a9804"

def call_tool(tool_name, arguments):
    """调用 MCP 工具"""
    # Step 1: Initialize session (for streamable-http)
    # For this gateway, JSON-RPC style calls seem to work
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        }
    }
    req = urllib.request.Request(
        MCP_URL,
        data=json.dumps(payload).encode('utf-8'),
        headers={
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        method='POST'
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        return {"error": str(e), "body": e.read().decode('utf-8')}
    except Exception as e:
        return {"error": str(e)}

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("用法: python3 dingtalk.py <tool_name> '<json_arguments>'")
        sys.exit(1)

    tool = sys.argv[1]
    args = json.loads(sys.argv[2])
    result = call_tool(tool, args)
    print(json.dumps(result, indent=2, ensure_ascii=False))
