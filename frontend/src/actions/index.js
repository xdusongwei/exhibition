import axios from 'axios'

export const EXECUTABLE = 'EXECUTABLE'
export const AIRPORT = 'AIRPORT'
export const WORKING = 'WORKING'

export const executablesUpdate = response => ({
  type: EXECUTABLE,
  response
})

export const airportUpdate = response => ({
  type: AIRPORT,
  response
})

export const workingUpdate = response => ({
  type: WORKING,
  response
})

export function fetchExecutables() {
  return function (dispatch) {
    return axios({url: '/interface/executables', method: 'get', timeout: 1000})
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
    return axios({url: '/interface/airport', method: 'get', timeout: 1000})
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
    return axios({url: '/interface/working', method: 'get', timeout: 1000})
      .then(({ data }) => {
        dispatch(workingUpdate(data));
      })
      .catch(r => {
        dispatch(workingUpdate(null));
      });
  };
}
