import { Component } from 'react';

class ExportPage extends Component {
    render() {
        return (
            <div>
                <div className="container">
                    <h4 className="text-start">服务端口</h4>
                    <h5 className="text-start">默认</h5>
                    <div className="row">
                        <div className="col border ">
                            <label>socks5:</label>
                        </div>
                        <div className="col border ">
                            <text>socks5://0.0.0.0:3456</text>
                        </div>
                    </div>
                    <hr/>
                    <div className="row">
                        <div className="col border ">
                            1 of 3
                        </div>
                        <div className="col border ">
                            2 of 3
                        </div>
                        <div className="col border ">
                            3 of 3
                        </div>
                    </div>
                </div>
            </div>
        );
    }
}

export default ExportPage;
