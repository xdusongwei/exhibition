import { Component } from 'react';
import { connect } from 'react-redux'
import { Link } from 'react-router-dom'
import { fetchExecutables } from "../actions";
import Executable from "../components/Executable";
import Loading from "../components/Loading"

class ExecutablePage extends Component {
    componentDidMount() {
        this.props.fetchExecutables()
    }

    refresh = (event) => {
        this.props.fetchExecutables()
    }

    displayItems(items){
        items = [...items]
        return items
    }

    render() {
        let executables = this.props.executables
        let loading = true
        
        if (Array.isArray(executables)) {
            loading = false
            executables = this.displayItems(executables)
        }

        return loading ?
            (
                <Loading />
            )
            :
            (
                <div>
                    <div className="row mt-2">
                        <div className="col-md-6">
                            <div className="alert alert-success" role="alert">绿色代表成功分析出软件类型</div>
                        </div>
                        <div className="col-md-6">
                            <div className="alert alert-light" role="alert">白色代表未能分析为已知的软件类型</div>
                        </div>
                    </div>
                    <div className="row mt-2">
                        <div className="col">
                            <div className="btn-group float-end" role="group" aria-label="pageBar">
                                <Link type="button" className="btn btn-primary ms-2" to="/executable/add">添加</Link>
                                <button type="button" className="btn btn-secondary ms-2" onClick={this.refresh}>刷新</button>
                            </div>
                        </div>
                    </div>
                    <div className="row mt-2">
                        {
                            executables.map((item, index) => <Executable key={index} index={index} item={item} />)
                        }
                    </div>
                </div>
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

export default connect(mapStateToProps, mapDispatchToProps)(ExecutablePage)
