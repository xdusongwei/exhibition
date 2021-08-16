import { Component } from 'react';
import { connect } from 'react-redux'
import axios from 'axios'
import { fetchExecutables } from "../actions";
import { Redirect } from 'react-router-dom'
import ErrorDetail from '../components/ErrorDetail'

class ExecutableEditPage extends Component {
    state = {
        enableSubmit: true,
        isFinish: false,
        error: null,
    }

    componentDidMount() {
        this.props.fetchExecutables()
    }

    submit = (e) => {
        e.preventDefault()
        const index = this.props.match.params.index
        const item = this.props.executables[index]
        if(item.path === e.target.elements.location.value){
            this.setState({isFinish: true})
            return
        }
        this.setState({enableSubmit: false, error: null})
        const currentPath = item.path
        const newPath = e.target.elements.location.value
        const data = {
            path: currentPath,
            newPath: newPath,
        }
        axios({url: './interface/executables', data, method: 'post', timeout: 1000})
        .then(({ data }) => {
            this.setState({isFinish: true, enableSubmit: true, })
        })
        .catch(data => {
            console.error(data)
            this.setState({enableSubmit: true, error: data, })
        });
    }

    render() {
        const items = this.props.executables
        let loading = true
        let item = null
            
        if (Array.isArray(items)) {
            const index = this.props.match.params.index
            item = this.props.executables[index]
            loading = item ? false : true
        }

        if (this.state.isFinish){
            return <Redirect to={{pathname: "../../executable", }} />
        }

        return loading ?
                (
                    <div>
                        <h5>请求中</h5>
                    </div>
                )
                :
                (
                    <form onSubmit={this.submit}>
                        <div className="mb-3">
                            <label htmlFor="location" className="form-label">位置</label>
                            <input type="input" className="form-control" id="location" defaultValue={item.path} required={true} />
                            <ErrorDetail e={this.state.error} />
                        </div>
                        <div className="mb-3">
                            <button type="submit" className="btn btn-primary" disabled={!this.state.enableSubmit}>保存</button>
                        </div>
                    </form>
                );
    }
}

const mapStateToProps = state => {
    const { executables, } = state

    return {
        executables,
    }
}

const mapDispatchToProps = (dispatch) => {
    return {
        fetchExecutables: () => {
            dispatch(fetchExecutables())
        }
    }
}

export default connect(mapStateToProps, mapDispatchToProps)(ExecutableEditPage)
