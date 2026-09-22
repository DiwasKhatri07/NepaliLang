"""
NepaliCode HTTP Library (anurodh)
Python requests-like API for HTTP requests
"""

import urllib.request
import urllib.parse
import urllib.error
import json
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass


@dataclass
class Response:
    """HTTP response object"""
    status: int
    text: str
    headers: Dict[str, str]
    content: bytes
    _json_data: Optional[Dict[str, Any]] = None
    
    @property
    def ok(self) -> bool:
        return 200 <= self.status < 300
    
    def json(self) -> Dict[str, Any]:
        if self._json_data is None:
            self._json_data = json.loads(self.text)
        return self._json_data


class Session:
    """HTTP session with cookie support"""
    def __init__(self):
        self.cookies: Dict[str, str] = {}
        self.headers: Dict[str, str] = {
            'User-Agent': 'NepaliCode/0.1.0'
        }
    
    def request(self, method: str, url: str, 
                data: Optional[Union[Dict[str, Any], str]] = None,
                json_data: Optional[Dict[str, Any]] = None,
                headers: Optional[Dict[str, str]] = None,
                params: Optional[Dict[str, Any]] = None,
                timeout: int = 30) -> Response:
        """Make HTTP request"""
        # Prepare URL with parameters
        if params:
            url = f"{url}?{urllib.parse.urlencode(params)}"
        
        # Prepare headers
        req_headers = self.headers.copy()
        if headers:
            req_headers.update(headers)
        
        # Prepare body
        body = None
        if json_data:
            body = json.dumps(json_data).encode('utf-8')
            req_headers['Content-Type'] = 'application/json'
        elif data:
            if isinstance(data, dict):
                body = urllib.parse.urlencode(data).encode('utf-8')
                req_headers['Content-Type'] = 'application/x-www-form-urlencoded'
            else:
                body = data.encode('utf-8')
        
        # Create request
        req = urllib.request.Request(url, data=body, headers=req_headers, method=method)
        
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                status = response.status
                text = response.read().decode('utf-8')
                content = response.read()
                response_headers = dict(response.headers)
                
                return Response(status, text, response_headers, content)
        except urllib.error.HTTPError as e:
            return Response(e.code, e.read().decode('utf-8'), dict(e.headers), b'')
        except urllib.error.URLError as e:
            raise Exception(f"Request failed: {e.reason}")
    
    def get(self, url: str, params: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None, timeout: int = 30) -> Response:
        return self.request('GET', url, params=params, headers=headers, timeout=timeout)
    
    def post(self, url: str, data: Optional[Union[Dict[str, Any], str]] = None,
             json_data: Optional[Dict[str, Any]] = None,
             headers: Optional[Dict[str, str]] = None, timeout: int = 30) -> Response:
        return self.request('POST', url, data=data, json_data=json_data, headers=headers, timeout=timeout)
    
    def put(self, url: str, data: Optional[Union[Dict[str, Any], str]] = None,
            json_data: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None, timeout: int = 30) -> Response:
        return self.request('PUT', url, data=data, json_data=json_data, headers=headers, timeout=timeout)
    
    def delete(self, url: str, headers: Optional[Dict[str, str]] = None, timeout: int = 30) -> Response:
        return self.request('DELETE', url, headers=headers, timeout=timeout)
    
    def patch(self, url: str, data: Optional[Union[Dict[str, Any], str]] = None,
              json_data: Optional[Dict[str, Any]] = None,
              headers: Optional[Dict[str, str]] = None, timeout: int = 30) -> Response:
        return self.request('PATCH', url, data=data, json_data=json_data, headers=headers, timeout=timeout)


# Module-level functions using default session
_default_session = Session()

def get(url: str, params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None, timeout: int = 30) -> Response:
    return _default_session.get(url, params=params, headers=headers, timeout=timeout)

def post(url: str, data: Optional[Union[Dict[str, Any], str]] = None,
          json_data: Optional[Dict[str, Any]] = None,
          headers: Optional[Dict[str, str]] = None, timeout: int = 30) -> Response:
    return _default_session.post(url, data=data, json_data=json_data, headers=headers, timeout=timeout)

def put(url: str, data: Optional[Union[Dict[str, Any], str]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None, timeout: int = 30) -> Response:
    return _default_session.put(url, data=data, json_data=json_data, headers=headers, timeout=timeout)

def delete(url: str, headers: Optional[Dict[str, str]] = None, timeout: int = 30) -> Response:
    return _default_session.delete(url, headers=headers, timeout=timeout)

def patch(url: str, data: Optional[Union[Dict[str, Any], str]] = None,
          json_data: Optional[Dict[str, Any]] = None,
          headers: Optional[Dict[str, str]] = None, timeout: int = 30) -> Response:
    return _default_session.patch(url, data=data, json_data=json_data, headers=headers, timeout=timeout)

def request(method: str, url: str, **kwargs) -> Response:
    return _default_session.request(method, url, **kwargs)


# For interpreter context
_module_dict = {
    'get': get,
    'post': post,
    'put': put,
    'delete': delete,
    'patch': patch,
    'request': request,
    'Session': Session,
    'Response': Response,
}


# For interpreter context
_module_dict = {
    'get': get,
    'post': post,
    'put': put,
    'delete': delete,
    'patch': patch,
    'request': request,
    'Session': Session,
    'Response': Response,
}