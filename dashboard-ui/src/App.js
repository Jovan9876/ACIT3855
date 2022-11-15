import logo from './logo.png';
import './App.css';

import EndpointAudit from './components/EndpointAudit'
import ServiceAudit from './components/ServiceAudit'
import AppStats from './components/AppStats'

function App() {

    const endpoints = ["weight", "step"]
    const services = ["reciever", "storage", "processing", "audit"]

    const rendered_endpoints = endpoints.map((endpoint) => {
        return <EndpointAudit key={endpoint} endpoint={endpoint}/>
    })

    const running_services = services.map((service) => {
        return <ServiceAudit key={service} service={service}/>
    })

    return (
        <div className="App">
            <img src={logo} className="App-logo" alt="logo" height="150px" width="400px"/>
            <div>
                <AppStats/>
                <h1>Audit Endpoints</h1>
                {rendered_endpoints}
                <h1>Service Health</h1>
                {running_services}
            </div>
        </div>
    );

}



export default App;
