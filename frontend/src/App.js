import { Route } from 'react-router-dom'
import ExportPage from './pages/Export'
import Executable from './pages/Executable'
import ExecutableEdit from './pages/ExecutableEdit'
import ExecutableAdd from './pages/ExecutableAdd'
import AirportPage from './pages/Airport'
import AirportAddPage from './pages/AirportAdd'
import WorkingPage from './pages/Working'
import ExportAddPage from './pages/ExportAdd'
import NodePage from './pages/Node'
import NodeAddPage from './pages/NodeAdd'
import SettingsPage from './pages/Settings'

function App() {
  return (
    <div className="App">
        <div>
          <main role="main">
            <div className="text-muted">
              <div className="container">
                <Route exact={true} path="/" component={ExportPage} />
                <Route exact={true} path="/airport" component={AirportPage} />
                <Route path="/airport/add" component={AirportAddPage} />
                <Route exact={true} path="/node" component={NodePage} />
                <Route  path="/node/add" component={NodeAddPage} />
                <Route exact={true} path="/export" component={ExportPage} />
                <Route exact={true} path="/export/add" component={ExportAddPage} />
                <Route exact={true} path="/executable" component={Executable} />
                <Route path="/executable/edit/:index" component={ExecutableEdit}/>
                <Route path="/executable/add" component={ExecutableAdd}/>
                <Route exact={true} path="/working" component={WorkingPage}/>
                <Route exact={true} path="/settings" component={SettingsPage}/>
              </div>
            </div>
          </main>
        </div>
      </div>
  );
}

export default App;
