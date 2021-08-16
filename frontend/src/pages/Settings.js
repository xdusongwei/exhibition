import { Component } from 'react';
import axios from 'axios'
import { Redirect } from 'react-router-dom'
import ErrorDetail from '../components/ErrorDetail'

class SettingsPage extends Component {
    state = {
        enableSubmit: false,
        isFinish: false,
        error: null,
        testUrl: '',
        exportRebootPeriod: 0,
        workingPortPoolStart: 9000,
        workingPortPoolEnd: 9999,
    }

    componentDidMount() {
        axios({url: './interface/settings', method: 'get', timeout: 1000})
        .then(({ data }) => {
            const settings = data.settings
            this.setState({
                enableSubmit: true, 
                testUrl: settings.testUrl,
                exportRebootPeriod: settings.exportRebootPeriod,
                workingPortPoolStart: settings.workingPortRangeStart,
                workingPortPoolEnd: settings.workingPortRangeEnd,
            })
        })
        .catch(data => {
            console.error(data)
            this.setState({enableSubmit: false, error: data, })
        })
    }

    submit = (event) => {
        event.preventDefault()
        const elements = event.target.elements
        const testUrl = elements.testUrl.value
        const exportRebootPeriod = elements.exportRebootPeriod.value
        const portPoolStart = elements.portPoolStart.value
        const portPoolEnd = elements.portPoolEnd.value
        let data = {
            testUrl: testUrl,
            exportRebootPeriod: parseInt(exportRebootPeriod),
            workingPortRangeStart: parseInt(portPoolStart),
            workingPortRangeEnd: parseInt(portPoolEnd),
        }

        axios({url: './interface/settings', data, method: 'post', timeout: 1000})
        .then(({ data }) => {
            this.setState({isFinish: true, enableSubmit: true, })
        })
        .catch(data => {
            console.error(data)
            this.setState({enableSubmit: true, error: data, })
        })
        this.setState({enableSubmit: false, error: null})
    }

    exportRebootPeriodChanged = (event) => {
        this.setState({
            exportRebootPeriod: event.target.value,
        })
    }

    workingPortPoolStartChanged = (event) => {
        this.setState({
            workingPortPoolStart: event.target.value,
        })
    }

    workingPortPoolEndChanged = (event) => {
        this.setState({
            workingPortPoolEnd: event.target.value,
        })
    }

    render() {
        const state = this.state

        if (state.isFinish){
            return <Redirect to={{pathname: '../', }} />
        }

        return <form onSubmit={this.submit}>
                    <div className="mb-3">
                        <div>
                            <h5 className="mt-4">基本设置</h5>
                            <label htmlFor="testUrl" className="form-label">测试链接</label>
                            <input type="input" className="form-control" id="testUrl" defaultValue={this.state.testUrl} required={true} />
                            <label htmlFor="exportRebootPeriod" className="form-label">外露服务重启间隔(秒)</label>
                            <input type="number" className="form-control" id="exportRebootPeriod" min={0} value={this.state.exportRebootPeriod} onChange={this.exportRebootPeriodChanged} required={true}/>
                            <label htmlFor="portPoolStart" className="form-label">工作节点端口池范围</label>
                            <div className="input-group mb-3">
                                <input type="number" className="form-control" placeholder="起始端口号" id="portPoolStart" aria-label="portPoolStart" min={1} max={65536} value={this.state.workingPortPoolStart} onChange={this.workingPortPoolStartChanged}/>
                                <span className="input-group-text">-</span>
                                <input type="number" className="form-control" placeholder="结束端口号" id="portPoolEnd" aria-label="portPoolEnd" min={1} max={65536}value={this.state.workingPortPoolEnd}  onChange={this.workingPortPoolEndChanged}/>
                            </div>
                            <hr/>
                            <ErrorDetail e={state.error} />
                        </div>
                        <div className="mb-3">
                            <button type="submit" className="btn btn-primary" disabled={!state.enableSubmit}>保存</button>
                        </div>
                    </div>
                </form>
    }
}

export default SettingsPage
