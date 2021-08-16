import { Component } from 'react';

class ErrorDetail extends Component {
    render() {
        const e = this.props.e
        let status = null
        let statusText = null
        let error = "服务异常"
        if(e){
            if(typeof(e) === 'object'){
                if(e.response){
                    status = e.response.status
                    statusText = e.response.statusText
                    if(e.response.data.error){
                        error = e.response.data.error
                    }
                }
            }
        }
        return e ? (
            <div className="mt-2 alert alert-danger" role="alert"><p>Status: {status}</p><p>{statusText}</p><p>{error}</p></div>
        ): null
    }
}

export default ErrorDetail
