import { Component } from 'react';
import { connect } from 'react-redux'
import { Link } from 'react-router-dom'
import { fetchCustomNodes } from "../actions";
import Node from "../components/Node";
import Loading from "../components/Loading"

class NodePage extends Component {
    componentDidMount() {
        this.props.fetchCustomNodes()
    }

    refresh = (event) => {
        this.props.fetchCustomNodes()
    }

    displayItems(items){
        items = [...items]
        return items
    }

    render() {
        let customNodes = this.props.customNodes
        let loading = true
        
        if (Array.isArray(customNodes)) {
            loading = false
            customNodes = this.displayItems(customNodes)
        }

        return loading ?
            (
                <Loading />
            )
            :
            (
                <div>
                    <div className="row mt-2">
                        <div className="col">
                            <div className="btn-group float-end" role="group" aria-label="pageBar">
                                <Link type="button" className="btn btn-primary ms-2" to="/node/add">添加</Link>
                                <button type="button" className="btn btn-secondary ms-2" onClick={this.refresh}>刷新</button>
                            </div>
                        </div>
                    </div>
                    <div className="row mt-2">
                        {
                            customNodes.map((item) => <Node key={item.id} item={item} />)
                        }
                    </div>
                </div>
            );
    }
}

const mapStateToProps = state => {
    const { customNodes, } = state

    return {
        customNodes,
    }
}

const mapDispatchToProps = (dispatch) => {
    return {
        fetchCustomNodes: () => {
            dispatch(fetchCustomNodes())
        }
    }
}

export default connect(mapStateToProps, mapDispatchToProps)(NodePage)
