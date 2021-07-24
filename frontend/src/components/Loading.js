import { Component } from 'react';

class Loading extends Component {
    render() {
        return (
            <div className="row mt-2">
                <div className="col">
                    <h5 className="text-center">请求中</h5>
                </div>
            </div>
        )
    }
}

export default Loading
