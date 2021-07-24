import { Component } from 'react'
import { NavLink } from 'react-router-dom'

class NavBar extends Component {
    render() {
        return (
            <nav className="navbar navbar-expand-lg navbar-light bg-light">
                <div className="container-fluid">
                    <NavLink exact to='/' className="navbar-brand">exhibition</NavLink>
                    <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
                        <span className="navbar-toggler-icon"></span>
                    </button>
                    <div className="collapse navbar-collapse" id="navbarSupportedContent">
                        <ul className="navbar-nav me-auto mb-2 mb-lg-0">
                            <li className="nav-item">
                                <NavLink exact activeClassName='active' to='/export' className="nav-link" aria-current="page">外露服务</NavLink>
                            </li>
                            <li className="nav-item">
                                <NavLink exact activeClassName='active' to='/working' className="nav-link" aria-current="page">工作节点</NavLink>
                            </li>
                            <li className="nav-item">
                                <NavLink exact activeClassName='active' to='/airport' className="nav-link" aria-current="page">机场</NavLink>
                            </li>
                            <li className="nav-item">
                                <NavLink exact activeClassName='active' to='/executable' className="nav-link" aria-current="page">软件</NavLink>
                            </li>
                            <li className="nav-item">
                                <NavLink exact activeClassName='active' to='/settings' className="nav-link" aria-current="page">设置</NavLink>
                            </li>
                        </ul>
                    </div>
                </div>
            </nav>
        )
    }
}

export default NavBar
