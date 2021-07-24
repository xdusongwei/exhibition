import { Route } from 'react-router-dom'
import ExportPage from './pages/Export'
import Executable from './pages/Executable'
import ExecutableEdit from './pages/ExecutableEdit'
import ExecutableAdd from './pages/ExecutableAdd'
import AirportPage from './pages/Airport'
import AirportAddPage from './pages/AirportAdd'
import WorkingPage from './pages/Working'

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
                <Route path="/export" component={ExportPage} />
                <Route exact={true} path="/executable" component={Executable} />
                <Route path="/executable/edit/:index" component={ExecutableEdit}/>
                <Route path="/executable/add" component={ExecutableAdd}/>
                <Route exact={true} path="/working" component={WorkingPage}/>
              </div>
            </div>
          </main>
        </div>
      </div>
  );
}

export default App;
