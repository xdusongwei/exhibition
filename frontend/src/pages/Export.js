import { Component } from 'react';
import { connect } from 'react-redux'
import { Link } from 'react-router-dom'
import { fetchExportNodes } from "../actions";
import Export from "../components/Export";
import Loading from "../components/Loading"

class ExportPage extends Component {
    componentDidMount() {
        this.props.fetchExportNodes()
    }

    refresh = (event) => {
        this.props.fetchExportNodes()
    }

    displayItems(items){
        items = [...items]
        return items
    }

    render() {
        let exportNodes = this.props.exportNodes
        let loading = true
        
        if (Array.isArray(exportNodes)) {
            loading = false
            exportNodes = this.displayItems(exportNodes)
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
                            <div className="alert alert-success" role="alert">绿色代表外露服务正常服务</div>
                        </div>
                        <div className="col-md-6">
                            <div className="alert alert-danger" role="alert">红色代表外露服务未运行</div>
                        </div>
                    </div>
                    <div className="row mt-2">
                        <div className="col">
                            <div className="btn-group float-end" role="group" aria-label="pageBar">
                                <Link type="button" className="btn btn-primary ms-2" to="/export/add">添加</Link>
                                <button type="button" className="btn btn-secondary ms-2" onClick={this.refresh}>刷新</button>
                            </div>
                        </div>
                    </div>
                    <div className="row mt-2">
                        {
                            exportNodes.map((item) => <Export key={item.settings.id} item={item} />)
                        }
                    </div>
                </div>
            );
    }
}

const mapStateToProps = state => {
    const { exportNodes, } = state

    return {
        exportNodes,
    }
}

const mapDispatchToProps = (dispatch) => {
    return {
        fetchExportNodes: () => {
            dispatch(fetchExportNodes())
        }
    }
}

export default connect(mapStateToProps, mapDispatchToProps)(ExportPage)
