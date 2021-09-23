import { Component } from 'react';
import axios from 'axios'
import { Redirect } from 'react-router-dom'
import { v4 as uuidv4 } from 'uuid';
import ErrorDetail from '../components/ErrorDetail'

class ExportAddPage extends Component {
    state = {
        enableSubmit: true,
        isFinish: false,
        currentProxy: 'VMESS',
        error: null,
        obfuscatingValue: '',
        showAlterId: true,
        showUuid: true,
        showObfuscating: true,
        showPath: false,
        showUser: false,
        showPassword: false,
        showFlow: false,
        showTls: true,
        showCertSecretPath: false,
        showCertPublicPath: false,
        showUsage: false,
        showMethod: false,
        tlsValue: 'none',
        methodValue: 'chacha20-ietf-poly1305',
    }

    submit = (event) => {
        event.preventDefault()
        const elements = event.target.elements
        const name = elements.name.value
        const host = elements.host.value
        const port = elements.port.value
        const proxy = elements.proxy.value
        const obfuscating = this.state.obfuscatingValue
        const selectCount = elements.selectCount.value
        const includeAirportNameRegex = elements.includeAirportNameRegex.value
        const includeWorkingNameRegex = elements.includeWorkingNameRegex.value
        const excludeAirportNameRegex = elements.excludeAirportNameRegex.value
        const excludeWorkingNameRegex = elements.excludeWorkingNameRegex.value
        let data = {
            name: name,
            host: host,
            port: port,
            proxy: proxy,
            obfuscating: obfuscating,
            selectCount: selectCount,
            includeAirportNameRegex: includeAirportNameRegex,
            includeWorkingNameRegex: includeWorkingNameRegex,
            excludeAirportNameRegex: excludeAirportNameRegex,
            excludeWorkingNameRegex: excludeWorkingNameRegex,
        }
        if(this.state.showAlterId){
            const alterId = elements.alterId.value
            data.alterId = alterId
        }
        if(this.state.showUuid){
            const uuid = elements.uuid.value
            data.uuid = uuid
        }
        if(this.state.showPath){
            const path = elements.path.value
            data.path = path
        }
        if(this.state.showUser){
            const user = elements.user.value
            data.user = user
        }
        if(this.state.showPassword){
            const password = elements.password.value
            data.password = password
        }
        if(elements.method){
            const method = elements.method.value
            data.method = method
        }
        if(elements.tls){
            const security = elements.security.value
            data.security = security
        }
        if(elements.usage){
            const usage = elements.usage.value
            data.usage = usage
        }
        if(elements.keyFile){
            const keyFile = elements.keyFile.value
            data.keyFile = keyFile
        }
        if(elements.certificateFile){
            const certificateFile = elements.certificateFile.value
            data.certificateFile = certificateFile
        }
        if(elements.flow){
            const flow = elements.flow.value
            data.flow = flow
        }
        axios({url: './interface/export', data, method: 'put', timeout: 1000})
        .then(({ data }) => {
            this.setState({isFinish: true, enableSubmit: true, })
        })
        .catch(data => {
            console.error(data)
            this.setState({enableSubmit: true, error: data, })
        })
        this.setState({enableSubmit: false, error: null})
    }

    proxyChanged = (event) => {
        const value = event.target.value
        if(value === 'VMESS'){
            this.setState({
                showAlterId: true,
                showUuid: true,
                showObfuscating: true,
                showUser: false,
                showPassword: false,
                showFlow: false,
                showTls: true,
                showMethod: false,
            })
        }
        if(value === 'VLESS'){
            this.setState({
                showAlterId: false,
                showUuid: true,
                showObfuscating: false,
                showUser: false,
                showPassword: false,
                showFlow: true,
                showTls: true,
                showMethod: false,
            })
        }
        if(value === 'TROJAN'){
            this.setState({
                showAlterId: false,
                showUuid: false,
                showObfuscating: false,
                showUser: false,
                showPassword: true,
                showFlow: false,
                showTls: false,
            })
        }
        if(value === 'SOCKS5'){
            this.setState({
                showAlterId: false,
                showUuid: false,
                showObfuscating: false,
                showUser: true,
                showPassword: true,
                showFlow: false,
                showTls: false,
                showMethod: false,
            })
        }
        if(value === 'HTTP'){
            this.setState({
                showAlterId: false,
                showUuid: false,
                showObfuscating: false,
                showUser: true,
                showPassword: true,
                showFlow: false,
                showTls: false,
                showMethod: false,
            })
        }
        if(value === 'SHADOWSOCKS'){
            this.setState({
                showAlterId: false,
                showUuid: false,
                showObfuscating: true,
                showUser: false,
                showPassword: true,
                showFlow: false,
                showTls: true,
                showMethod: true,
            })
        }
        this.setState({currentProxy: value})
    }

    obfuscatingChanged = (event) => {
        const value = event.target.value
        this.setState({obfuscatingValue: value})
        if(value === ''){
            this.setState({showPath: false})
        }
        if(value === 'WEBSOCKET'){
            this.setState({showPath: true})
        }
    }

    tlsChanged = (event) => {
        this.setState({tlsValue: event.target.value})
    }

    methodChanged = (event) => {
        this.setState({methodValue: event.target.value})
    }

    render() {
        const state = this.state

        if (state.isFinish){
            return <Redirect to={{pathname: '../export', }} />
        }

        return <form onSubmit={this.submit}>
                    <div className="mb-3">
                        <div>
                            <h5 className="mt-4">基本设置</h5>
                            <label htmlFor="name" className="form-label">*名称</label>
                            <input type="input" className="form-control" id="name" required={true} />
                            <label htmlFor="host" className="form-label">*绑定地址</label>
                            <input type="input" className="form-control" id="host" required={true} defaultValue="0.0.0.0" />
                            <label htmlFor="port" className="form-label">*绑定端口</label>
                            <input type="number" className="form-control" id="port" required={true} min="1" max="65536" />
                            <label htmlFor="proxy" className="form-label">*协议</label>
                            <select className="form-select form-control" id="proxy" defaultValue="VMESS" onChange={this.proxyChanged}>
                                <option value="VMESS">VMess</option>
                                <option value="VLESS" >VLESS</option>
                                <option value="SOCKS5">SOCKS5</option>
                                <option value="HTTP">HTTP</option>
                                <option value="SHADOWSOCKS">SHADOWSOCKS</option>
                            </select>
                            <hr/>
                        </div>
                        {state.showAlterId || state.showUuid || state.showUser || state.showPassword ? (
                        <div>
                            <h5 className="mt-4">协议设置</h5>
                            { state.showAlterId ? 
                            <div>
                                <label htmlFor="alterId" className="form-label">alterId</label>
                                <input type="input" className="form-control" id="alterId"  defaultValue="" />
                            </div> : null }
                            { state.showUuid ?
                            <div>
                                <label htmlFor="uuid" className="form-label">*uuid</label>
                                <input type="input" className="form-control" id="uuid" required={true} defaultValue={uuidv4()} />
                            </div> : null }
                            { state.showUser ?
                            <div>
                                <label htmlFor="user" className="form-label">user</label>
                                <input type="input" className="form-control" id="user" defaultValue="" />
                            </div> : null }
                            { state.showPassword ?
                            <div>
                                <label htmlFor="password" className="form-label">*password</label>
                                <input type="input" className="form-control" id="password" defaultValue="" required={true}/>
                            </div> : null }
                            { state.showMethod ?
                            <div>
                                <label htmlFor="method" className="form-label">*method</label>
                                <select className="form-select form-control" id="method" value={state.methodValue} onChange={this.methodChanged}>
                                    <option value="none">none</option>
                                    <option value="plain">plain</option>
                                    <option value="aes-256-gcm">aes-256-gcm</option>
                                    <option value="aes-128-gcm">aes-128-gcm</option>
                                    <option value="chacha20-poly1305">chacha20-poly1305</option>
                                    <option value="chacha20-ietf-poly1305">chacha20-ietf-poly1305</option>
                                </select> 
                            </div> : null 
                            }
                            { state.showTls ?
                            <div>
                                <label htmlFor="security" className="form-label">*security</label>
                                <select className="form-select form-control" id="security" value={state.tlsValue} onChange={this.tlsChanged}>
                                    <option value="none">none</option>
                                    <option value="tls">tls</option>
                                    { state.currentProxy === 'VLESS' ? <option value="xtls">xtls</option> : null }
                                </select> 
                            </div> : null 
                            }
                            { state.showTls && (state.tlsValue === 'tls' || state.tlsValue === 'xtls' ) ? 
                            <div>
                                <label htmlFor="usage" className="form-label">*usage</label>
                                <select className="form-select form-control" id="usage" defaultValue="encipherment">
                                    <option value="encipherment">encipherment</option>
                                    <option value="verify">verify</option>
                                    <option value="issue">issue</option>
                                </select> 
                                <label htmlFor="keyFile" className="form-label">*keyFile</label>
                                <input type="input" className="form-control" id="keyFile" defaultValue="" required={true} />
                                <label htmlFor="certificateFile" className="form-label">*certificateFile</label>
                                <input type="input" className="form-control" id="certificateFile" defaultValue="" required={true} />
                            </div> : null
                            }
                            { state.showFlow ?
                            <div>
                                <label htmlFor="flow" className="form-label">*flow</label>
                                <select className="form-select form-control" id="flow" defaultValue="xtls-rprx-direct">
                                    <option value="xtls-rprx-origin">xtls-rprx-origin</option>
                                    <option value="xtls-rprx-direct">xtls-rprx-direct</option>
                                </select> 
                            </div> : null 
                            }
                            <hr/>
                        </div>) : null }
                        {state.showObfuscating ? (
                            <div>
                                <h5 className="mt-4">混淆设置</h5>
                                <div>
                                    <label htmlFor="obfuscating" className="form-label">混淆</label>
                                    <select className="form-select form-control" id="obfuscating" onChange={this.obfuscatingChanged} value={state.obfuscatingValue}>
                                        <option value="">不混淆</option>
                                        <option value="WEBSOCKET">WebSocket</option>
                                    </select>
                                </div>
                                { state.showPath ? 
                                <div>
                                    <label htmlFor="path" className="form-label">*Path</label>
                                    <input type="input" className="form-control" id="path" required={true} />
                                </div> : null }
                                <hr/>
                            </div>) : null }
                        <div>
                            <h5 className="mt-4">工作节点设置</h5>
                            <div>
                                <label htmlFor="selectCount" className="form-label">*每个机场最多可选择工作节点数量</label>
                                <input type="number" className="form-control" id="selectCount" required={true} defaultValue="3" min="1"/>
                            </div>
                            <div>
                                <label htmlFor="includeAirportNameRegex" className="form-label">包含工作节点, 按机场名称正则匹配</label>
                                <input type="input" className="form-control" id="includeAirportNameRegex" defaultValue="" />
                            </div>
                            <div>
                                <label htmlFor="includeWorkingNameRegex" className="form-label">包含工作节点, 按工作节点名称正则匹配</label>
                                <input type="input" className="form-control" id="includeWorkingNameRegex" defaultValue="" />
                            </div>
                            <div>
                                <label htmlFor="excludeAirportNameRegex" className="form-label">排除工作节点, 按机场名称正则匹配</label>
                                <input type="input" className="form-control" id="excludeAirportNameRegex" defaultValue="" />
                            </div>
                            <div>
                                <label htmlFor="excludeWorkingNameRegex" className="form-label">排除工作节点, 按工作节点名称正则匹配</label>
                                <input type="input" className="form-control" id="excludeWorkingNameRegex" defaultValue="" />
                            </div>
                            <hr/>
                        </div>
                        <ErrorDetail e={state.error} />
                    </div>
                    <div className="mb-3">
                        <button type="submit" className="btn btn-primary" disabled={!state.enableSubmit}>创建</button>
                    </div>
                </form>
    }
}

export default ExportAddPage
