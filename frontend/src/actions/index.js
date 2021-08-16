import axios from 'axios'

export const EXECUTABLE = 'EXECUTABLE'
export const AIRPORT = 'AIRPORT'
export const WORKING = 'WORKING'
export const EXPORT = 'EXPORT'
export const NODE = 'NODE'

export const executablesUpdate = response => ({
  type: EXECUTABLE,
  response,
})

export const airportUpdate = response => ({
  type: AIRPORT,
  response,
})

export const workingUpdate = response => ({
  type: WORKING,
  response,
})

export const exportUpdate = response => ({
  type: EXPORT,
  response,
})

export const nodeUpdate = response => ({
  type: NODE,
  response,
})

export function fetchExecutables() {
  return function (dispatch) {
    return axios({url: './interface/executables', method: 'get', timeout: 1000})
      .then(({ data }) => {
        dispatch(executablesUpdate(data));
      })
      .catch(r => {
        dispatch(executablesUpdate(null));
      });
  };
}

export function fetchAirportNodes() {
  return function (dispatch) {
    return axios({url: './interface/airport', method: 'get', timeout: 1000})
      .then(({ data }) => {
        dispatch(airportUpdate(data));
      })
      .catch(r => {
        dispatch(airportUpdate(null));
      });
  };
}

export function fetchWorkingNodes() {
  return function (dispatch) {
    return axios({url: './interface/working', method: 'get', timeout: 1000})
      .then(({ data }) => {
        dispatch(workingUpdate(data));
      })
      .catch(r => {
        dispatch(workingUpdate(null));
      });
  };
}

export function fetchExportNodes() {
  return function (dispatch) {
    return axios({url: './interface/export', method: 'get', timeout: 1000})
      .then(({ data }) => {
        dispatch(exportUpdate(data));
      })
      .catch(r => {
        dispatch(exportUpdate(null));
      });
  };
}

export function fetchCustomNodes() {
  return function (dispatch) {
    return axios({url: './interface/node', method: 'get', timeout: 1000})
      .then(({ data }) => {
        dispatch(nodeUpdate(data));
      })
      .catch(r => {
        dispatch(nodeUpdate(null));
      });
  };
}


