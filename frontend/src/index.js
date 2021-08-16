import React from 'react';
import ReactDOM from 'react-dom';
import { HashRouter } from 'react-router-dom';
import { createStore, applyMiddleware } from 'redux'
import { Provider } from 'react-redux'
import thunk from 'redux-thunk'
import { createLogger } from 'redux-logger'
import reducer from './reducers'
import './index.css';
import NavBar from "./components/NavBar";
import App from './App';
import reportWebVitals from './reportWebVitals';

const middleware = [ thunk ]
if (process.env.NODE_ENV !== 'production') {
  middleware.push(createLogger())
}

const store = createStore(
  reducer,
  { 
    executables: null,
    airportNodes: null,
    workingNodes: null,
    exportNodes: null,
    customNodes: null,
  },
  applyMiddleware(...middleware)
)

ReactDOM.render(
  <React.StrictMode>
    <Provider store={store}>
      <HashRouter>
        <NavBar />
        <App />
      </HashRouter>
    </Provider>
  </React.StrictMode>,
  document.getElementById('root')
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
