import React, { useEffect, useState } from 'react'
import '../App.css';

export default function AppStats() {
    const [isLoaded, setIsLoaded] = useState(false);
    const [stats, setStats] = useState({});
    const [error, setError] = useState(null)

	const getStats = () => {
	
        fetch(`http://acit-3855.eastus.cloudapp.azure.com:8100/stats`)
            .then(res => res.json())
            .then((result)=>{
				console.log("Received Stats")
                setStats(result);
                setIsLoaded(true);
            },(error) =>{
                setError(error)
                setIsLoaded(true);
            })
    }
    useEffect(() => {
		const interval = setInterval(() => getStats(), 2000); // Update every 2 seconds
		return() => clearInterval(interval);
    }, [getStats]);

    if (error){
        return (<div className={"error"}>Error found when fetching from API</div>)
    } else if (isLoaded === false){
        return(<div>Loading...</div>)
    } else if (isLoaded === true){
        return(
            <div>
                <h1>Latest Stats</h1>
                <table className={"StatsTable"}>
					<tbody>
						<tr>
							<th>Step Reading</th>
							<th>Weight Reading</th>
						</tr>
						<tr>
							<td># Step: {stats['numStepReadings']}</td>
							<td># Weight: {stats['numWeightReadings']}</td>

						</tr>
						<tr>
							<td colspan="2">Avg number of steps: {stats['avgNumSteps']}</td>
						</tr>
						<tr>
							<td colspan="2">Avg weight lost: {stats['avgWeightLost']}</td>
						</tr>
						<tr>
							<td colspan="2">Avg floors climbed: {stats['avgFloorsClimbed']}</td>
						</tr>
						<tr>
							<td colspan="2">Avg calories burned: {stats['avgCaloriesBurned']}</td>
						</tr>
						<tr>
							<td colspan="2">Max distance: {stats['maxDistance']}</td>
						</tr>
						<tr>
							<td colspan="2">Max weight lost: {stats['maxWeightLost']}</td>
						</tr>
						<tr>
							<td colspan="2">Avg Elevation: {stats['avgElevation']}</td>
						</tr>
					</tbody>
                </table>
                <h3>Last Updated: {stats['lastUpdated']}</h3>

            </div>
        )
    }
}
