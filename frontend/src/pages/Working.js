import { Component } from 'react';
import { connect } from 'react-redux'
import axios from 'axios'
import { fetchWorkingNodes } from "../actions";
import Working from "../components/Working";
import Loading from "../components/Loading"

class WorkingPage extends Component {
    state = {
        disabledAllTest: false,
    }

    componentDidMount() {
        this.props.fetchWorkingNodes()
    }

    refresh = (event) => {
        this.props.fetchWorkingNodes()
    }

    allTest = (event) => {
        const data = {
            workingId: null,
        }
        axios({url: './interface/working/test', data, method: 'post', timeout: 1000})
        .then(({ data }) => {
            
        })
        .catch(data => {
            console.error(data)
        });
        this.setState({disabledAllTest: true})
    }

    displayItems(items){
        items = [...items]
        return items
    }

    render() {
        let workingNodes = this.props.workingNodes
        let loading = true
        
        if (Array.isArray(workingNodes)) {
            loading = false
            workingNodes = this.displayItems(workingNodes)
        }

        return loading ?
            (
                <Loading />
            )
            :
            (
                <div>
                    <div className="row mt-2">
                        <div className="col-md-4">
                            <div className="alert alert-success" role="alert">绿色代表节点被外露服务使用</div>
                        </div>
                        <div className="col-md-4">
                            <div className="alert alert-light" role="alert">白色代表节点测试可以联通</div>
                        </div>
                        <div className="col-md-4">
                            <div className="alert alert-danger" role="alert">红色代表节点无成功连接</div>
                        </div>
                    </div>
                    <div className="row mt-2">
                        <div className="col">
                            <div className="btn-group float-end" role="group" aria-label="pageBar">
                                <button type="button" className="btn btn-success ms-2" onClick={this.allTest} disabled={this.state.disabledAllTest}>全部测速</button>
                                <button type="button" className="btn btn-secondary ms-2" onClick={this.refresh}>刷新</button>
                            </div>
                        </div>
                    </div>
                    <div className="row mt-2">
                        {
                            workingNodes.map((item) => <Working key={item.settings.id} item={item} />)
                        }
                    </div>
                </div>
            );
    }
}

const mapStateToProps = state => {
    const { workingNodes, } = state

    return {
        workingNodes,
    }
}

const mapDispatchToProps = (dispatch) => {
    return {
        fetchWorkingNodes: () => {
            dispatch(fetchWorkingNodes())
        }
    }
}

export default connect(mapStateToProps, mapDispatchToProps)(WorkingPage)
