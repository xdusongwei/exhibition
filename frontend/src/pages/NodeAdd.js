import { Component } from 'react';
import axios from 'axios'
import { Redirect } from 'react-router-dom'
import ErrorDetail from '../components/ErrorDetail'

class NodeAddPage extends Component {
    state = {
        enableSubmit: true,
        isFinish: false,
        currentProxy: 'VMESS',
        error: null,
        obfuscatingValue: '',
        tlsValue: 'none',
        showAlterId: true,
        showUuid: true,
        showObfuscating: true,
        showPath: false,
        showUser: false,
        showPassword: false,
        showSecurity: true,
        showEncryption: false,
        showFlow: false,
        showEncryptMethod: false,
        showTls: true,
    }

    submit = (event) => {
        event.preventDefault()
        const elements = event.target.elements
        const name = elements.name.value
        const host = elements.host.value
        const port = elements.port.value
        const proxy = elements.proxy.value
        const obfuscating = this.state.obfuscatingValue
        const tls = this.state.tlsValue
        let data = {
            name: name,
            host: host,
            port: port,
            proxy: proxy,
            obfuscating: obfuscating,
            tls: tls,
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
        if(this.state.showSecurity){
            const security = elements.security.value
            data.security = security
        }
        if(this.state.showEncryption){
            const encryption = elements.encryption.value
            data.encryption = encryption
        }
        if(this.state.showFlow){
            const flow = elements.flow.value
            data.flow = flow
        }
        if(this.state.showEncryptMethod){
            const encryptMethod = elements.encryptMethod.value
            data.encryptMethod = encryptMethod
        }

        axios({url: './interface/node', data, method: 'put', timeout: 1000})
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
                showSecurity: true,
                showEncryption: false,
                showFlow: false,
                showEncryptMethod: false,
                showTls: true,
            })
        }
        if(value === 'VLESS'){
            this.setState({
                showAlterId: false,
                showUuid: true,
                showObfuscating: true,
                showUser: false,
                showPassword: false,
                showSecurity: false,
                showEncryption: true,
                showFlow: false,
                showEncryptMethod: false,
                showTls: true,
            })
        }
        if(value === 'TROJAN'){
            this.setState({
                showAlterId: false,
                showUuid: false,
                showObfuscating: false,
                showUser: false,
                showPassword: true,
                showSecurity: false,
                showEncryption: false,
                showFlow: false,
                showEncryptMethod: false,
                showTls: false,
            })
        }
        if(value === 'SHADOWSOCKS'){
            this.setState({
                showAlterId: false,
                showUuid: false,
                showObfuscating: false,
                showUser: false,
                showPassword: true,
                showSecurity: false,
                showEncryption: false,
                showFlow: false,
                showEncryptMethod: true,
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
                showSecurity: false,
                showEncryption: false,
                showFlow: false,
                showEncryptMethod: false,
                showTls: false,
            })
        }
        if(value === 'HTTP'){
            this.setState({
                showAlterId: false,
                showUuid: false,
                showObfuscating: false,
                showUser: true,
                showPassword: true,
                showSecurity: false,
                showEncryption: false,
                showFlow: false,
                showEncryptMethod: false,
                showTls: false,
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
        if(value === 'HTTP'){
            this.setState({showPath: true})
        }
    }

    tlsChanged = (event) => {
        const value = event.target.value
        this.setState({tlsValue: value})
        if(value === ''){
            this.setState({showFlow: false})
        }
        if(value === 'tls'){
            this.setState({showFlow: false})
        }
        if(value === 'xtls'){
            this.setState({showFlow: true})
        }
    }

    render() {
        const state = this.state

        if (state.isFinish){
            return <Redirect to={{pathname: '../node', }} />
        }

        return <form onSubmit={this.submit}>
                    <div className="mb-3">
                        <div>
                            <h5 className="mt-4">基本设置</h5>
                            <label htmlFor="name" className="form-label">*名称</label>
                            <input type="input" className="form-control" id="name" required={true} />
                            <label htmlFor="host" className="form-label">*连接地址</label>
                            <input type="input" className="form-control" id="host" required={true} />
                            <label htmlFor="port" className="form-label">*连接端口</label>
                            <input type="number" className="form-control" id="port" required={true} min="1" max="65536" />
                            <label htmlFor="proxy" className="form-label">*协议</label>
                            <select className="form-select form-control" id="proxy" defaultValue="VMESS" onChange={this.proxyChanged}>
                                <option value="VMESS">VMess</option>
                                <option value="VLESS">VLESS</option>
                                <option value="SHADOWSOCKS">Shadowsocks</option>
                                <option value="TROJAN">Trojan</option>
                                <option value="SOCKS5">SOCKS5</option>
                                <option value="HTTP">HTTP</option>
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
                            </div> : null 
                            }
                            { state.showUuid ?
                            <div>
                                <label htmlFor="uuid" className="form-label">*uuid</label>
                                <input type="input" className="form-control" id="uuid" required={true} />
                            </div> : null 
                            }
                            { state.showUser ?
                            <div>
                                <label htmlFor="user" className="form-label">user</label>
                                <input type="input" className="form-control" id="user" defaultValue="" />
                            </div> : null 
                            }
                            { state.showPassword ?
                            <div>
                                <label htmlFor="password" className="form-label">{state.currentProxy === 'TROJAN' || state.currentProxy === 'SHADOWSOCKS' ? '*' : null}password</label>
                                <input type="input" className="form-control" id="password" defaultValue="" required={true}/>
                            </div> : null 
                            }
                            { state.showSecurity ?
                            <div>
                                <label htmlFor="security" className="form-label">*security</label>
                                <select className="form-select form-control" id="security" defaultValue="auto">
                                    <option value="auto">auto</option>
                                    <option value="none">none</option>
                                    <option value="zero">zero</option>
                                    <option value="aes-128-gcm">aes-128-gcm</option>
                                    <option value="chacha20-poly1305">chacha20-poly1305</option>
                                </select>
                            </div> : null 
                            }
                            { state.showEncryption ?
                            <div>
                                <label htmlFor="encryption" className="form-label">*encryption</label>
                                <select className="form-select form-control" id="encryption" defaultValue="none">
                                    <option value="none">none</option>
                                </select> 
                            </div> : null 
                            }
                            { state.showTls ?
                            <div>
                                <label htmlFor="tls" className="form-label">*(X)TLS</label>
                                <select className="form-select form-control" id="tls" value={state.tlsValue} onChange={this.tlsChanged}>
                                    <option value="none">不使用</option>
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
                                <label htmlFor="keyFile" className="form-label">keyFile</label>
                                <input type="input" className="form-control" id="keyFile" defaultValue="" />
                                <label htmlFor="certificateFile" className="form-label">certificateFile</label>
                                <input type="input" className="form-control" id="certificateFile" defaultValue="" />
                            </div> : null
                            }
                            { state.showFlow ?
                            <div>
                                <label htmlFor="flow" className="form-label">*flow</label>
                                <select className="form-select form-control" id="flow" defaultValue="xtls-rprx-direct">
                                    <option value="xtls-rprx-origin">xtls-rprx-origin</option>
                                    <option value="xtls-rprx-origin-udp443">xtls-rprx-origin-udp443</option>
                                    <option value="xtls-rprx-direct">xtls-rprx-direct</option>
                                    <option value="xtls-rprx-direct-udp443">xtls-rprx-direct-udp443</option>
                                    <option value="xtls-rprx-splice">xtls-rprx-splice</option>
                                    <option value="xtls-rprx-splice-udp443">xtls-rprx-splice-udp443</option>
                                </select> 
                            </div> : null 
                            }
                            { state.showEncryptMethod ?
                            <div>
                                <label htmlFor="encryptMethod" className="form-label">*encrypt_method</label>
                                <select className="form-select form-control" id="encryptMethod" defaultValue="chacha20-ietf-poly1305">
                                    <option value="rc4-md5">rc4-md5</option>
                                    <option value="aes-128-gcm">aes-128-gcm</option>
                                    <option value="aes-256-gcm">aes-256-gcm</option>
                                    <option value="aes-128-cfb">aes-128-cfb</option>
                                    <option value="aes-192-cfb">aes-192-cfb</option>
                                    <option value="aes-256-cfb">aes-256-cfb</option>
                                    <option value="aes-128-ctr">aes-128-ctr</option>
                                    <option value="aes-192-ctr">aes-192-ctr</option>
                                    <option value="aes-256-ctr">aes-256-ctr</option>
                                    <option value="camellia-128-cfb">camellia-128-cfb</option>
                                    <option value="camellia-192-cfb">camellia-192-cfb</option>
                                    <option value="camellia-256-cfb">camellia-256-cfb</option>
                                    <option value="bf-cfb">bf-cfb</option>
                                    <option value="chacha20-ietf-poly1305">chacha20-ietf-poly1305</option>
                                    <option value="xchacha20-ietf-poly1305">xchacha20-ietf-poly1305</option>
                                    <option value="salsa20">salsa20</option>
                                    <option value="chacha20">chacha20</option>
                                    <option value="chacha20-ietf">chacha20-ietf</option>
                                </select> 
                            </div> : null 
                            }
                            <hr/>
                        </div>) : null }
                        <hr/>
                        {state.showObfuscating ? (
                            <div>
                                <h5 className="mt-4">混淆设置</h5>
                                <div>
                                    <label htmlFor="obfuscating" className="form-label">混淆</label>
                                    <select className="form-select form-control" id="obfuscating" onChange={this.obfuscatingChanged} value={state.obfuscatingValue}>
                                        <option value="">无</option>
                                        <option value="WEBSOCKET">WebSocket</option>
                                        <option value="HTTP">HTTP/2</option>
                                    </select>
                                </div>
                                { state.showPath ? 
                                <div>
                                    <label htmlFor="path" className="form-label">*Path</label>
                                    <input type="input" className="form-control" id="path" required={true} />
                                </div> : null }
                                <hr/>
                            </div>) : null }
                        <ErrorDetail e={state.error} />
                    </div>
                    <div className="mb-3">
                        <button type="submit" className="btn btn-primary" disabled={!state.enableSubmit}>创建</button>
                    </div>
                </form>
    }
}

export default NodeAddPage
