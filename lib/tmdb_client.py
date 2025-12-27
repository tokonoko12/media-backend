import requests
import os


class TMDBClient:
    BASE_URL = "https://api.themoviedb.org/3"
    IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"
    BACKDROP_BASE_URL = "https://image.tmdb.org/t/p/original"

    def __init__(self):
        self.api_key = os.environ.get("TMDB_API_KEY")
        if not self.api_key:
            print("Warning: TMDB_API_KEY not found in environment")

    def _get(self, endpoint, params={}):
        params["api_key"] = self.api_key
        response = requests.get(f"{self.BASE_URL}{endpoint}", params=params)
        response.raise_for_status()
        return response.json()

    def get_external_id(self, tmdb_id, media_type):
        """Fetch external ID (IMDb) for a given TMDB ID."""
        try:
            data = self._get(f"/{media_type}/{tmdb_id}/external_ids")
            return data.get("imdb_id")
        except:
            return None

    def _format_media(self, item, media_type=None):
        # Determine type if not provided (helpful for 'all' endpoints)
        m_type = media_type or item.get("media_type")
        if m_type == "tv":
            m_type = "series"
        
        # Map fields
        title = item.get("title") if m_type == "movie" else item.get("name")
        release_date = item.get("release_date") if m_type == "movie" else item.get("first_air_date")
        
        return {
            "id": str(item.get("id")), # Keep ID as string for consistency
            "tmdb_id": item.get("id"),
            "title": title,
            "poster_path": f"{self.IMAGE_BASE_URL}{item.get('poster_path')}" if item.get("poster_path") else None,
            "backdrop_path": f"{self.BACKDROP_BASE_URL}{item.get('backdrop_path')}" if item.get("backdrop_path") else None,
            "media_type": m_type,
            "release_date": release_date,
            "overview": item.get("overview"),
            "vote_average": item.get("vote_average")
        }

    def _format_credits(self, credits):
        if not credits:
            return {}
            
        cast = credits.get("cast", [])
        crew = credits.get("crew", [])
        
        for member in cast:
            if member.get("profile_path"):
                member["profile_path"] = f"{self.IMAGE_BASE_URL}{member['profile_path']}"
                
        for member in crew:
            if member.get("profile_path"):
                member["profile_path"] = f"{self.IMAGE_BASE_URL}{member['profile_path']}"
                
        return {"cast": cast, "crew": crew}



    def get_trending_home(self):
        # Trending All Day
        data = self._get("/trending/all/day")
        results = data.get("results", [])
        return [self._format_media(item) for item in results]

    def get_popular_movies(self):
        data = self._get("/movie/popular")
        results = data.get("results", [])
        return [self._format_media(item, "movie") for item in results]

    def get_popular_series(self):
        data = self._get("/tv/popular")
        results = data.get("results", [])
        return [self._format_media(item, "series") for item in results]

    def get_now_playing(self):
        data = self._get("/movie/now_playing")
        results = data.get("results", [])
        return [self._format_media(item, "movie") for item in results]

    def get_top_rated(self):
        data = self._get("/movie/top_rated")
        results = data.get("results", [])
        return [self._format_media(item, "movie") for item in results]

    def get_bollywood_movies(self):
        # Hindi movies, Region IN
        data = self._get("/discover/movie", params={
            "with_original_language": "hi",
            "region": "IN",
            "sort_by": "popularity.desc"
        })
        results = data.get("results", [])
        return [self._format_media(item, "movie") for item in results]

    def get_south_indian_movies(self):
        # Tamil, Telugu, Malayalam, Kannada
        data = self._get("/discover/movie", params={
            "with_original_language": "ta|te|ml|kn",
            "region": "IN",
            "sort_by": "popularity.desc"
        })
        results = data.get("results", [])
        return [self._format_media(item, "movie") for item in results]

    def get_indian_tv_shows(self):
        # TV Shows from India
        data = self._get("/discover/tv", params={
            "with_origin_country": "IN",
            "sort_by": "popularity.desc"
        })
        results = data.get("results", [])
        return [self._format_media(item, "series") for item in results]

    def get_movies_by_genre(self, genre_id, page=1):
        data = self._get("/discover/movie", params={
            "with_genres": str(genre_id),
            "sort_by": "popularity.desc",
            "page": page
        })
        results = data.get("results", [])
        return {
            "results": [self._format_media(item, "movie") for item in results],
            "page": data.get("page"),
            "total_pages": data.get("total_pages"),
            "total_results": data.get("total_results")
        }

    def get_series_by_genre(self, genre_id, page=1):
        data = self._get("/discover/tv", params={
            "with_genres": str(genre_id),
            "sort_by": "popularity.desc",
            "page": page
        })
        results = data.get("results", [])
        return {
            "results": [self._format_media(item, "series") for item in results],
            "page": data.get("page"),
            "total_pages": data.get("total_pages"),
            "total_results": data.get("total_results")
        }

    def get_movie_details(self, tmdb_id):
        data = self._get(f"/movie/{tmdb_id}", params={
            "append_to_response": "credits,recommendations,external_ids"
        })
        # Format base info
        formatted = self._format_media(data, "movie")
        # Add extra info
        formatted["credits"] = self._format_credits(data.get("credits"))
        formatted["recommendations"] = [self._format_media(item, "movie") for item in data.get("recommendations", {}).get("results", [])]
        formatted["genres"] = data.get("genres")
        formatted["runtime"] = data.get("runtime")
        # External IDs
        formatted["external_ids"] = data.get("external_ids")
        return formatted

    def get_series_details(self, tmdb_id):
        data = self._get(f"/tv/{tmdb_id}", params={
            "append_to_response": "credits,recommendations,season/1,external_ids"
        })
        formatted = self._format_media(data, "series")
        formatted["credits"] = self._format_credits(data.get("credits"))
        formatted["recommendations"] = [self._format_media(item, "series") for item in data.get("recommendations", {}).get("results", [])]
        formatted["genres"] = data.get("genres")
        formatted["number_of_episodes"] = data.get("number_of_episodes")
        formatted["number_of_seasons"] = data.get("number_of_seasons")
        formatted["external_ids"] = data.get("external_ids")
        return formatted

    def get_season_details(self, tmdb_id, season_number):
        data = self._get(f"/tv/{tmdb_id}/season/{season_number}")
        # Identify episodes
        episodes = data.get("episodes", [])
        formatted_episodes = []
        for ep in episodes:
            formatted_episodes.append({
                "id": str(ep.get("id")),
                "tmdb_id": ep.get("id"),
                "title": ep.get("name"),
                "overview": ep.get("overview"),
                "still_path": f"{self.IMAGE_BASE_URL}{ep.get('still_path')}" if ep.get("still_path") else None,
                "air_date": ep.get("air_date"),
                "episode_number": ep.get("episode_number"),
                "season_number": ep.get("season_number"),
                "vote_average": ep.get("vote_average"),
                "runtime": ep.get("runtime")
            })
        
        return {
            "id": str(data.get("id")),
            "name": data.get("name"),
            "overview": data.get("overview"),
            "poster_path": f"{self.IMAGE_BASE_URL}{data.get('poster_path')}" if data.get("poster_path") else None,
            "season_number": data.get("season_number"),
            "air_date": data.get("air_date"),
            "episodes": formatted_episodes
        }

    def search_multi(self, query, page=1):
        data = self._get("/search/multi", params={
            "query": query,
            "page": page,
            "include_adult": "false",
            "language": "en-US"
        })
        results = data.get("results", [])
        # Filter only movie and tv
        filtered = [item for item in results if item.get("media_type") in ["movie", "tv"]]
        
        return {
            "results": [self._format_media(item) for item in filtered],
            "page": data.get("page"),
            "total_pages": data.get("total_pages"),
            "total_results": data.get("total_results")
        }

    def get_media_basic_details(self, tmdb_id, media_type):
        """Fetch basic details for a media item (movie/series) without extra appends."""
        endpoint = f"/movie/{tmdb_id}" if media_type == 'movie' else f"/tv/{tmdb_id}"
        try:
            data = self._get(endpoint)
            return self._format_media(data, media_type)
        except Exception as e:
            # Fallback if item not found or API error, return minimal info
            print(f"Error fetching details for {media_type} {tmdb_id}: {e}")
            return {
                "id": str(tmdb_id),
                "tmdb_id": tmdb_id,
                "media_type": media_type,
                "title": "Unknown Title",
                "error": "Could not load details"
            }
