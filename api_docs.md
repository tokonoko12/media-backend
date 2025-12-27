# API Documentation

Base URL: `http://localhost:8090`

## Authentication

### Register
Create a new user account.

- **Endpoint**: `POST /auth/register`
- **Headers**: `Content-Type: application/json`
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "yourpassword",
    "username": "user123",
    "full_name": "Test User"
  }
  ```
- **Response (201 Created)**:
  ```json
  {
    "message": "User registered successfully",
    "user": {
      "id": 1,
      "username": "user123",
      "email": "user@example.com"
    },
    "session": {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ..."
    }
  }
  ```

### Login
Authenticate a user and get an access token.

- **Endpoint**: `POST /auth/login`
- **Headers**: `Content-Type: application/json`
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "yourpassword"
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "message": "Login successful",
    "user": {
      "id": 1,
      "username": "user123",
      "email": "user@example.com",
      "full_name": "Test User"
    },
    "session": {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ..."
    }
  }
  ```

### Get Current User
Get details of the currently authenticated user.

- **Endpoint**: `GET /auth/me`
- **Headers**: `Authorization: Bearer <access_token>`
- **Response (200 OK)**:
  ```json
  {
    "user": {
      "id": 1,
      "username": "user123",
      "email": "user@example.com",
      "full_name": "Test User",
      "avatar_url": null,
      "created_at": "2023-10-27T10:00:00.000000"
    }
  }
  ```

### Logout
End the session (Client should remove the token).

- **Endpoint**: `POST /auth/logout`
- **Headers**: `Authorization: Bearer <access_token>`
- **Response (200 OK)**:
  ```json
  {
    "message": "Logged out successfully"
  }
  ```


---

## Catalog

### Search
Search for movies and TV series.

- **Endpoint**: `GET /search?q=<query>`
- **Headers**: `Authorization: Bearer <access_token>`
- **Response (200 OK)**:
  ```json
  {
      "results": [
          {
              "id": "123",
              "tmdb_id": 123,
              "title": "Avatar",
              "media_type": "movie",
              ...
          }
      ]
  }
  ```

### Home Screen
Get trending movies and series mixed.

- **Endpoint**: `GET /catalog/home`
- **Headers**: `Authorization: Bearer <access_token>`
- **Response (200 OK)**:
  ```json
  {
      "featured": [
          {
              "id": "12345",
              "tmdb_id": 12345,
              "title": "Movie Title",
              "poster_path": "https://image.tmdb.org/t/p/w500/...",
              "backdrop_path": "https://image.tmdb.org/t/p/w500/...",
              "media_type": "movie",
              "release_date": "2023-11-20",
              "overview": " Movie overview...",
              "vote_average": 7.5
          }
      ],
      "sections": [
          {
              "title": "Recent Arrivals",
              "items": [
                  {
                      "id": "67890",
                      "tmdb_id": 67890,
                      "title": "Series Title",
                      "poster_path": "...",
                      "backdrop_path": "...",
                      "media_type": "series",
                      "release_date": "2023-10-10",
                      "overview": "...",
                      "vote_average": 8.0
                  },
                  ...
              ]
          },
          {
              "title": "Bollywood Hits",
              "items": [ ... ]
          },
          {
              "title": "Global Hits",
              "items": [ ... ]
          },
          {
              "title": "South Indian Cinema",
              "items": [ ... ]
          },
          {
              "title": "World TV Hits",
              "items": [ ... ]
          },
          {
              "title": "Indian TV Shows",
              "items": [ ... ]
          },
          {
              "title": "Top Rated Archive",
              "items": [ ... ]
          }
      ]
  }
  ```

### Popular Movies
Get popular movies.

- **Endpoint**: `GET /catalog/movies`
- **Headers**: `Authorization: Bearer <access_token>`
- **Response (200 OK)**:
  ```json
  {
      "sections": [
          {
              "title": "Popular Movies",
              "items": [
                  {
                      "id": "12345",
                      "tmdb_id": 12345,
                      "title": "Movie Title",
                      "poster_path": "...",
                      "backdrop_path": "...",
                      "media_type": "movie",
                      "release_date": "2023-11-20",
                      "overview": "...",
                      "vote_average": 7.5
                  }
              ]
          },
          {
              "title": "Action",
              "items": [ ... ]
          }
           // ... other genres
      ]
  }
  ```

### Popular Series
Get popular TV series.

- **Endpoint**: `GET /catalog/series`
- **Headers**: `Authorization: Bearer <access_token>`
- **Response (200 OK)**:
  ```json
  {
      "sections": [
          {
              "title": "Popular Series",
              "items": [
                  {
                      "id": "67890",
                      "tmdb_id": 67890,
                      "title": "Series Title",
                      "poster_path": "...",
                      "backdrop_path": "...",
                      "media_type": "series",
                      "release_date": "2023-10-10",
                      "overview": "...",
                      "vote_average": 8.0
                  }
              ]
          },
          {
              "title": "Action & Adventure",
              "items": [ ... ]
          }
           // ... other genres
      ]
  }
  ```

### Movie Details
Get detailed information for a movie.

- **Endpoint**: `GET /details/movies/<tmdb_id>`
- **Headers**: `Authorization: Bearer <access_token>`
- **Response (200 OK)**:
  ```json
  {
      "id": "123",
      "tmdb_id": 123,
      "title": "Movie Title",
      "overview": "...",
      "poster_path": "...",
      "backdrop_path": "...",
      "release_date": "2023-01-01",
      "media_type": "movie",
      "genres": [
          {"id": 28, "name": "Action"}
      ],
      "runtime": 120,
      "vote_average": 8.5,
      "credits": {
          "cast": [
              {"id": 1, "name": "Actor Name", "character": "Role", "profile_path": "..."}
          ],
          "crew": [...]
      },
      "recommendations": [
           { 
             "id": "999", 
             "title": "Recommended Movie", 
             "media_type": "movie",
             ...
           }
      ],
      "streams_url": "http://localhost:8090/streams/movies/tt1234567"
  }
  ```

### Series Details
Get detailed information for a TV series.

- **Endpoint**: `GET /details/series/<tmdb_id>`
- **Headers**: `Authorization: Bearer <access_token>`
- **Response (200 OK)**:
  ```json
  {
      "id": "456",
      "tmdb_id": 456,
      "name": "Series Title",
      "overview": "...",
      "poster_path": "...",
      "backdrop_path": "...",
      "first_air_date": "2023-01-01",
      "media_type": "series",
      "genres": [
          {"id": 18, "name": "Drama"}
      ],
      "number_of_seasons": 2,
      "number_of_episodes": 20,
      "vote_average": 8.5,
      "credits": {
          "cast": [...],
          "crew": [...]
      },
      "recommendations": [...],
      "seasons": [
          {
              "id": 100,
              "name": "Season 1",
              "season_number": 1,
              "poster_path": "..."
          }
      ]
  }
  ```

### Season Details
Get details for a specific season of a series (including episodes and stream URLs).

- **Endpoint**: `GET /details/series/<tmdb_id>/season/<season_number>`
- **Headers**: `Authorization: Bearer <access_token>`
- **Response (200 OK)**:
  ```json
  {
      "id": "789",
      "name": "Season 1",
      "overview": "...",
      "poster_path": "...",
      "season_number": 1,
      "air_date": "2023-01-01",
      "episodes": [
          {
              "id": "1001",
              "tmdb_id": 1001,
              "title": "Episode 1",
              "overview": "...",
              "still_path": "...",
              "episode_number": 1,
              "season_number": 1,
              "vote_average": 8.0,
              "streams_url": "http://localhost:8090/streams/series/tt456789/1/1"
          },
          ...
      ]
  }
  ```

---

## Watchlist

### Add to Watchlist
Add a movie or series to the user's watchlist.

- **Endpoint**: `POST /watchlist`
- **Headers**: 
  - `Content-Type: application/json`
  - `Authorization: Bearer <access_token>`
- **Request Body**:
  ```json
  {
    "media_id": "tt1234567",
    "media_type": "movie"  // or "series"
  }
  ```
- **Response (201 Created or 200 OK if exists)**:
  ```json
  {
    "message": "Added to watchlist",
    "item": {
      "media_id": "tt1234567",
      "media_type": "movie"
    }
  }
  ```

### Get Watchlist
Retrieve all items in the user's watchlist.

- **Endpoint**: `GET /watchlist`
- **Headers**: `Authorization: Bearer <access_token>`
- **Response (200 OK)**:
  ```json
  {
    "watchlist": [
      {
        "media_id": "tt1234567",
        "media_type": "movie",
        "added_at": "2023-10-27T10:00:00.000000"
      },
      {
         "media_id": "tt7654321",
         "media_type": "series",
         "added_at": "2023-10-28T11:30:00.000000"
      }
    ]
  }
  ```

### Remove from Watchlist
Delete an item from the watchlist.

- **Endpoint**: `DELETE /watchlist/<media_id>`
- **Headers**: `Authorization: Bearer <access_token>`
- **Response (200 OK)**:
  ```json
  {
    "message": "Removed from watchlist"
  }
  ```

---

## Watch History

### Update History
Record progress for a movie or episode. This is an upsert operation (creates if new, updates if exists).

- **Endpoint**: `POST /history`
- **Headers**: 
  - `Content-Type: application/json`
  - `Authorization: Bearer <access_token>`
### Update Watch History
**POST** `/history`

**Headers:**
- `Authorization: Bearer <token>`

**Body:**
```json
{
  "media_id": "123",
  "media_type": "movie",
  "progress": 1200,      // Seconds watched
  "duration": 5400,      // Total duration in seconds
  "season": 1,           // Required for series
  "episode": 1           // Required for series
}
```

**Response:**
```json
{
  "message": "History updated"
}
```

### Get Watch History
**GET** `/history`

**Headers:**
- `Authorization: Bearer <token>`

**Query Parameters:**
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20)

**Response:**
```json
{
  "history": [
    {
      "id": "123",
      "tmdb_id": 123,
      "media_type": "movie",
      "title": "Inception",
      "poster_path": "https://image.tmdb.org/t/p/w500/...",
      "backdrop_path": "https://image.tmdb.org/t/p/original/...",
      "overview": "...",
      "progress": 1200,
      "duration": 5400,
      "season": null,
      "episode": null,
      "last_watched_at": "2023-10-27T10:30:00"
    }
  ],
  "page": 1,
  "total_pages": 5,
  "total_results": 100
}
```

### Get History for Specific Media
**GET** `/history/media/<media_id>`

**Headers:**
- `Authorization: Bearer <token>`

**Query Parameters:**
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20)

**Response:**
```json
{
  "history": [
    {
      "id": "456",
      "tmdb_id": 456,
      "media_type": "series",
      "title": "Breaking Bad",
      "poster_path": "https://image.tmdb.org/t/p/w500/...",
      "season": 1,
      "episode": 1,
      "progress": 3000,
      "duration": 3600,
      "last_watched_at": "2023-10-26T20:00:00"
    }
  ],
  "page": 1,
  "total_pages": 4,
  "total_results": 62
}
```
