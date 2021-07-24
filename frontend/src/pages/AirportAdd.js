import { Component } from 'react';
import axios from 'axios'
import { Redirect } from 'react-router-dom'

class AirportAddPage extends Component {
    state = {
        enableSubmit: true,
        isFinish: false,
        error: null,
    }

    submit = (e) => {
        e.preventDefault()
        this.setState({enableSubmit: false, error: null})
        const name = e.target.elements.name.value
        const url = e.target.elements.url.value
        const data = {
            name: name,
            url: url,
        }
        axios({url: '/interface/airport', data, method: 'put', timeout: 1000})
        .then(({ data }) => {
            this.setState({isFinish: true, enableSubmit: true, })
        })
        .catch(data => {
            console.error(data)
            let error = "服务异常"
            if(data.response && data.response.data.error){
                error = data.response.data.error
            }
            this.setState({enableSubmit: true, error: error, })
        });
    }

    render() {
        if (this.state.isFinish){
            return <Redirect to={{pathname: "/airport", }} />
        }

        return <form onSubmit={this.submit}>
                    <div className="mb-3">
                        <label htmlFor="name" className="form-label">名称</label>
                        <input type="input" className="form-control" id="name" required={true} />
                        <label htmlFor="url" className="form-label">链接</label>
                        <input type="input" className="form-control" id="url" required={true} />
                        {this.state.error ? <div className="mt-2 alert alert-danger" role="alert">{this.state.error}</div> : null}
                    </div>
                    <div className="mb-3">
                        <button type="submit" className="btn btn-primary" disabled={!this.state.enableSubmit}>创建</button>
                    </div>
                </form>
    }
}

export default AirportAddPage
