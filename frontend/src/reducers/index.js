import { combineReducers } from 'redux'
import {
    EXECUTABLE,
    AIRPORT,
    WORKING,
    EXPORT,
    NODE,
  } from '../actions'

const executables = (state = [], action) => {
    switch (action.type) {
        case EXECUTABLE:
            if(action.response){
                return action.response.executables
            }
            else{
                return []
            }
        default:
            return state
    }
}

const airportNodes = (state = [], action) => {
    switch (action.type) {
        case AIRPORT:
            if(action.response){
                return action.response.airportNodes
            }
            else{
                return []
            }
        default:
            return state
    }
}

const workingNodes = (state = [], action) => {
    switch (action.type) {
        case WORKING:
            if(action.response){
                return action.response.workingNodes
            }
            else{
                return []
            }
        default:
            return state
    }
}

const exportNodes = (state = [], action) => {
    switch (action.type) {
        case EXPORT:
            if(action.response){
                return action.response.exportNodes
            }
            else{
                return []
            }
        default:
            return state
    }
}

const customNodes = (state = [], action) => {
    switch (action.type) {
        case NODE:
            if(action.response){
                return action.response.customNodes
            }
            else{
                return []
            }
        default:
            return state
    }
}

const rootReducer = combineReducers({
    executables,
    airportNodes,
    workingNodes,
    exportNodes,
    customNodes,
})

export default rootReducer
