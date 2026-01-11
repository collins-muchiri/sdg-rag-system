from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
import aiohttp
import asyncio

from config.settings import settings
from src.agents.transportation_agent import TransportationAgent

router = APIRouter()


@router.get("/transit/london")
async def get_london_transit_data():
    """Get real-time London transit data from TfL API"""
    
    if not settings.tfl_api_key:
        raise HTTPException(status_code=501, detail="TfL API key not configured")
    
    try:
        agent = TransportationAgent()
        data = await agent.get_london_transit_data()
        
        return {
            "city": "London",
            "data_source": "Transport for London",
            "timestamp": data.get("timestamp"),
            "transit_modes": data.get("transit_modes", []),
            "service_disruptions": data.get("disruptions", []),
            "sdg_relevance": {
                "goals": ["11", "13"],
                "metrics": ["public_transport_usage", "emissions_reduction", "accessibility"]
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching London transit data: {str(e)}")


@router.get("/ev/charging-stations")
async def get_ev_charging_stations(
    latitude: float = Query(..., description="Latitude for location-based search"),
    longitude: float = Query(..., description="Longitude for location-based search"),
    radius: int = Query(10, description="Search radius in kilometers")
):
    """Get EV charging stations from Open Charge Map API"""
    
    if not settings.open_charge_map_api_key:
        raise HTTPException(status_code=501, detail="Open Charge Map API key not configured")
    
    try:
        agent = TransportationAgent()
        stations = await agent.get_ev_charging_stations(latitude, longitude, radius)
        
        return {
            "location": {"latitude": latitude, "longitude": longitude},
            "radius_km": radius,
            "charging_stations": stations,
            "total_stations": len(stations),
            "sdg_relevance": {
                "goals": ["7", "11", "13"],
                "metrics": ["clean_energy_infrastructure", "sustainable_transport", "climate_action"]
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching EV charging stations: {str(e)}")


@router.get("/ride-sharing/uber")
async def get_uber_data(
    latitude: float = Query(..., description="Latitude"),
    longitude: float = Query(..., description="Longitude")
):
    """Get Uber ride-sharing data and pricing"""
    
    if not settings.uber_api_key:
        raise HTTPException(status_code=501, detail="Uber API key not configured")
    
    try:
        agent = TransportationAgent()
        data = await agent.get_uber_data(latitude, longitude)
        
        return {
            "location": {"latitude": latitude, "longitude": longitude},
            "services": data.get("products", []),
            "pricing": data.get("price_estimates", []),
            "availability": data.get("availability", {}),
            "sdg_relevance": {
                "goals": ["11"],
                "metrics": ["mobility_access", "shared_transport", "urban_planning"]
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching Uber data: {str(e)}")


@router.get("/aviation/flights")
async def get_aviation_data(
    airport_code: str = Query(..., description="IATA airport code"),
    flight_type: str = Query("departures", description="departures or arrivals")
):
    """Get real-time aviation data"""
    
    try:
        agent = TransportationAgent()
        data = await agent.get_aviation_data(airport_code, flight_type)
        
        return {
            "airport": airport_code,
            "flight_type": flight_type,
            "flights": data.get("flights", []),
            "timestamp": data.get("timestamp"),
            "sdg_relevance": {
                "goals": ["9", "11"],
                "metrics": ["connectivity", "economic_activity", "infrastructure_utilization"]
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching aviation data: {str(e)}")


@router.get("/maritime/vessels")
async def get_maritime_data(
    latitude: float = Query(..., description="Latitude"),
    longitude: float = Query(..., description="Longitude"),
    radius: int = Query(50, description="Search radius in kilometers")
):
    """Get maritime vessel tracking data"""
    
    try:
        agent = TransportationAgent()
        data = await agent.get_maritime_data(latitude, longitude, radius)
        
        return {
            "location": {"latitude": latitude, "longitude": longitude},
            "radius_km": radius,
            "vessels": data.get("vessels", []),
            "total_vessels": len(data.get("vessels", [])),
            "vessel_types": data.get("vessel_types", []),
            "sdg_relevance": {
                "goals": ["9", "14"],
                "metrics": ["maritime_traffic", "trade_volume", "shipping_efficiency"]
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching maritime data: {str(e)}")


@router.get("/sustainability/metrics")
async def get_transportation_sustainability_metrics():
    """Get aggregated transportation sustainability metrics"""
    
    try:
        agent = TransportationAgent()
        metrics = await agent.get_sustainability_metrics()
        
        return {
            "timestamp": metrics.get("timestamp"),
            "metrics": {
                "ev_infrastructure": metrics.get("ev_charging_stations", {}),
                "public_transport_usage": metrics.get("transit_data", {}),
                "emissions_data": metrics.get("emissions", {}),
                "sustainable_mobility": metrics.get("sustainable_mobility", {})
            },
            "sdg_mapping": {
                "7": "Affordable and Clean Energy",
                "9": "Industry, Innovation and Infrastructure",
                "11": "Sustainable Cities and Communities",
                "13": "Climate Action",
                "14": "Life Below Water"
            },
            "recommendations": metrics.get("recommendations", [])
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching sustainability metrics: {str(e)}")


@router.get("/dashboard")
async def get_transportation_dashboard():
    """Get comprehensive transportation dashboard for SDG monitoring"""
    
    try:
        # Fetch data from multiple sources
        tasks = []
        
        # Add API calls based on available keys
        if settings.tfl_api_key:
            tasks.append(get_london_transit_data())
        
        if settings.open_charge_map_api_key:
            # Use London coordinates as default
            tasks.append(get_ev_charging_stations(51.5074, -0.1278, 20))
        
        if settings.uber_api_key:
            tasks.append(get_uber_data(51.5074, -0.1278))
        
        # Execute all available tasks
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter successful results
        successful_results = [result for result in results if not isinstance(result, Exception)]
        
        return {
            "dashboard_title": "Transportation SDG Monitoring Dashboard",
            "last_updated": asyncio.get_event_loop().time(),
            "data_sources": len(successful_results),
            "data": successful_results,
            "sdg_goals_covered": ["7", "9", "11", "13", "14"],
            "status": "active"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating dashboard: {str(e)}")