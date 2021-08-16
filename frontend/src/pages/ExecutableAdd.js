import { Component } from 'react';
import axios from 'axios'
import { Redirect } from 'react-router-dom'
import ErrorDetail from '../components/ErrorDetail'

class ExecutableAddPage extends Component {
    state = {
        enableSubmit: true,
        isFinish: false,
        error: null,
    }

    submit = (e) => {
        e.preventDefault()
        this.setState({enableSubmit: false, error: null})
        const currentPath = e.target.elements.location.value
        const data = {
            path: currentPath,
        }
        axios({url: './interface/executables', data, method: 'put', timeout: 1000})
        .then(({ data }) => {
            this.setState({isFinish: true, enableSubmit: true, })
        })
        .catch(data => {
            console.error(data)
            this.setState({enableSubmit: true, error: data, })
        });
    }

    render() {
        if (this.state.isFinish){
            return <Redirect to={{pathname: "../executable", }} />
        }

        return <form onSubmit={this.submit}>
                    <div className="mb-3">
                        <label htmlFor="location" className="form-label">位置</label>
                        <input type="input" className="form-control" id="location" required={true} />
                        <ErrorDetail e={this.state.error} />
                    </div>
                    <div className="mb-3">
                        <button type="submit" className="btn btn-primary" disabled={!this.state.enableSubmit}>创建</button>
                    </div>
                </form>
    }
}

export default ExecutableAddPage
