import aiohttp
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime

from config.settings import settings


class TransportationAgent:
    def __init__(self):
        self.session = None
    
    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
    
    async def get_london_transit_data(self) -> Dict[str, Any]:
        """Get real-time London transit data from TfL API"""
        
        try:
            session = await self._get_session()
            
            # TfL Unified API endpoints
            endpoints = [
                "https://api.tfl.gov.uk/Line/Mode/tube,overground,dlr,tram/Status",
                "https://api.tfl.gov.uk/StopPoint/Mode/tube/Disruption",
                "https://api.tfl.govLine/Meta/Modes"
            ]
            
            results = {}
            
            for endpoint in endpoints:
                headers = {"app_key": settings.tfl_api_key} if settings.tfl_api_key else {}
                
                async with session.get(endpoint, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        endpoint_name = endpoint.split("/")[-1]
                        results[endpoint_name] = data
            
            return {
                "timestamp": datetime.now().isoformat(),
                "transit_data": results,
                "status": "success"
            }
        
        except Exception as e:
            return {
                "error": str(e),
                "status": "failed",
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_ev_charging_stations(self, latitude: float, longitude: float, radius: int) -> List[Dict[str, Any]]:
        """Get EV charging stations from Open Charge Map API"""
        
        try:
            session = await self._get_session()
            
            # Open Charge Map API
            url = f"https://api.openchargemap.io/v3/poi"
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "distance": radius,
                "distanceunit": "km",
                "maxresults": 100,
                "compact": "true",
                "verbose": "false"
            }
            
            if settings.open_charge_map_api_key:
                params["key"] = settings.open_charge_map_api_key
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Process and format the data
                    stations = []
                    for station in data:
                        station_info = {
                            "id": station.get("ID"),
                            "name": station.get("AddressInfo", {}).get("Title", "Unknown"),
                            "address": station.get("AddressInfo", {}).get("AddressLine1", ""),
                            "latitude": station.get("AddressInfo", {}).get("Latitude"),
                            "longitude": station.get("AddressInfo", {}).get("Longitude"),
                            "operator": station.get("OperatorInfo", {}).get("Title", "Unknown"),
                            "usage_type": station.get("UsageType", {}).get("Title", "Unknown"),
                            "status": station.get("StatusType", {}).get("Title", "Unknown"),
                            "number_of_points": station.get("NumberOfPoints", 0),
                            "power_output": self._extract_power_output(station)
                        }
                        stations.append(station_info)
                    
                    return stations
                
                else:
                    return []
        
        except Exception as e:
            print(f"Error fetching EV charging stations: {e}")
            return []
    
    def _extract_power_output(self, station: Dict) -> List[str]:
        """Extract power output information from station data"""
        
        power_outputs = []
        connections = station.get("Connections", [])
        
        for connection in connections:
            power_kw = connection.get("PowerKW")
            if power_kw:
                power_outputs.append(f"{power_kw}kW")
        
        return power_outputs
    
    async def get_uber_data(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Get Uber ride-sharing data"""
        
        try:
            session = await self._get_session()
            
            # Uber API endpoints
            products_url = f"https://api.uber.com/v1.2/products"
            price_url = f"https://api.uber.com/v1.2/estimates/price"
            
            headers = {
                "Authorization": f"Token {settings.uber_api_key}",
                "Content-Type": "application/json"
            }
            
            params = {"latitude": latitude, "longitude": longitude}
            
            # Get available products
            async with session.get(products_url, headers=headers, params=params) as response:
                products = []
                if response.status == 200:
                    data = await response.json()
                    products = data.get("products", [])
            
            # Get price estimates (requires destination)
            # For demo purposes, use a nearby destination
            dest_params = {
                "start_latitude": latitude,
                "start_longitude": longitude,
                "end_latitude": latitude + 0.01,
                "end_longitude": longitude + 0.01
            }
            
            price_estimates = []
            async with session.get(price_url, headers=headers, params=dest_params) as response:
                if response.status == 200:
                    data = await response.json()
                    price_estimates = data.get("prices", [])
            
            return {
                "products": products,
                "price_estimates": price_estimates,
                "timestamp": datetime.now().isoformat(),
                "location": {"latitude": latitude, "longitude": longitude}
            }
        
        except Exception as e:
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_aviation_data(self, airport_code: str, flight_type: str = "departures") -> Dict[str, Any]:
        """Get aviation data using ADS-B Exchange API"""
        
        try:
            session = await self._get_session()
            
            # ADS-B Exchange API (free tier)
            url = f"https://adsbexchange.com/api/v2/airport/{airport_code}"
            
            params = {
                "limit": 100,
                "type": flight_type
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    flights = []
                    for flight in data.get("ac", []):
                        flight_info = {
                            "flight_number": flight.get("flight", "").strip(),
                            "aircraft": flight.get("type", ""),
                            "altitude": flight.get("alt", ""),
                            "speed": flight.get("spd", ""),
                            "heading": flight.get("hd", ""),
                            "origin": flight.get("from", ""),
                            "destination": flight.get("to", ""),
                            "status": flight.get("gnd", "Airborne") if flight.get("gnd") != "1" else "On Ground"
                        }
                        flights.append(flight_info)
                    
                    return {
                        "airport": airport_code,
                        "flight_type": flight_type,
                        "flights": flights,
                        "total_flights": len(flights),
                        "timestamp": datetime.now().isoformat()
                    }
                
                else:
                    return {
                        "error": f"API returned status {response.status}",
                        "airport": airport_code,
                        "timestamp": datetime.now().isoformat()
                    }
        
        except Exception as e:
            return {
                "error": str(e),
                "airport": airport_code,
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_maritime_data(self, latitude: float, longitude: float, radius: int) -> Dict[str, Any]:
        """Get maritime vessel data"""
        
        try:
            session = await self._get_session()
            
            # Note: This would require a maritime API like AIS Hub or MarineTraffic
            # For demo purposes, return mock data structure
            
            # In production, you would use:
            # url = f"https://api.aishub.net/v2/vesselarea/username/key/lat/lon/radius"
            
            mock_vessels = [
                {
                    "mmsi": "123456789",
                    "name": "MV Example",
                    "type": "Cargo",
                    "latitude": latitude + 0.01,
                    "longitude": longitude + 0.01,
                    "speed": 12.5,
                    "heading": 180,
                    "destination": "Next Port"
                }
            ]
            
            return {
                "location": {"latitude": latitude, "longitude": longitude},
                "radius": radius,
                "vessels": mock_vessels,
                "total_vessels": len(mock_vessels),
                "timestamp": datetime.now().isoformat(),
                "note": "Mock data - requires maritime API subscription"
            }
        
        except Exception as e:
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_sustainability_metrics(self) -> Dict[str, Any]:
        """Get aggregated sustainability metrics"""
        
        try:
            # Collect data from various sources
            tasks = []
            
            if settings.tfl_api_key:
                tasks.append(self.get_london_transit_data())
            
            if settings.open_charge_map_api_key:
                # Use London coordinates as default
                tasks.append(self.get_ev_charging_stations(51.5074, -0.1278, 50))
            
            # Execute tasks
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            metrics = {
                "timestamp": datetime.now().isoformat(),
                "ev_charging_stations": {},
                "transit_data": {},
                "emissions": {},
                "sustainable_mobility": {},
                "recommendations": []
            }
            
            for result in results:
                if isinstance(result, Exception):
                    continue
                
                if "transit_data" in str(result):
                    metrics["transit_data"] = result
                elif "stations" in str(result):
                    metrics["ev_charging_stations"] = {
                        "total_stations": len(result),
                        "stations": result[:10]  # Sample of stations
                    }
            
            # Generate recommendations
            metrics["recommendations"] = self._generate_sustainability_recommendations(metrics)
            
            return metrics
        
        except Exception as e:
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _generate_sustainability_recommendations(self, metrics: Dict) -> List[str]:
        """Generate sustainability recommendations based on metrics"""
        
        recommendations = []
        
        # EV infrastructure recommendations
        ev_stations = metrics.get("ev_charging_stations", {}).get("total_stations", 0)
        if ev_stations < 50:
            recommendations.append("Consider expanding EV charging infrastructure to meet growing demand")
        
        # Transit system recommendations
        transit_data = metrics.get("transit_data", {})
        if transit_data:
            recommendations.append("Monitor public transit performance for optimization opportunities")
        
        # General recommendations
        recommendations.extend([
            "Implement real-time monitoring for transportation systems",
            "Focus on multi-modal transport integration",
            "Prioritize sustainable transport options in urban planning"
        ])
        
        return recommendations