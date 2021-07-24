import { Component } from 'react';
import { connect } from 'react-redux'
import { Link } from 'react-router-dom'
import { fetchWorkingNodes } from "../actions";
import Working from "../components/Working";
import Loading from "../components/Loading"

class WorkingPage extends Component {
    componentDidMount() {
        this.props.fetchWorkingNodes()
    }

    refresh = (event) => {
        this.props.fetchWorkingNodes()
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
                        <div className="col">
                            <div className="btn-group float-end" role="group" aria-label="pageBar">
                                <button type="button" className="btn btn-secondary ms-2" onClick={this.refresh}>刷新</button>
                            </div>
                        </div>
                    </div>
                    <div className="row mt-2">
                        {
                            workingNodes.map((item) => <Working key={item.id} item={item} />)
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
