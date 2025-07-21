# Laravel Route Annotations

A lightweight VS Code extension that displays route path annotations above Laravel route definitions in `routes/web.php` | `routes/api.php`.

## Features

- **Automatic Route Detection**: Scans `routes/web.php` | `routes/api.php` and detects Laravel route definitions (`Route::get`, `Route::post`, etc.)
- **Path Annotations**: Shows gray-colored decorations above each route with the full path: `🧩 Route Path: /users/{id}`
- **Route Group Support**: Handles `Route::group` with prefix parsing for nested routes
- **Toggle On/Off**: Use `Cmd+Shift+U` (Mac) or `Ctrl+Shift+U` (Windows) to toggle annotations
- **Real-time Updates**: Annotations update automatically as you edit your routes file

## Usage

1. Open a Laravel project in VS Code
2. Navigate to `routes/web.php` and `routes/api.php` or `routes/<any_nested_included_routes>`
3. Route annotations will appear automatically above each route definition
4. Use the keyboard shortcut to toggle annotations on/off

## Supported Route Methods

- `Route::get`
- `Route::post`
- `Route::put`
- `Route::delete`
- `Route::patch`
- `Route::options`
- `Route::any`

## Example

Given this routes file:

```php
// web.php

<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\HomeController;
use App\Http\Controllers\ProfileController;

Route::get('/', [HomeController::class, 'index']);
Route::get('/about', [HomeController::class, 'about']);

Route::group(['prefix' => 'user'], function () {
    Route::get('/profile', [ProfileController::class, 'show']);
    Route::post('/profile', [ProfileController::class, 'update']);
});
```

The extension will display:

```php
<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\HomeController;
use App\Http\Controllers\ProfileController;

Route::get('/', [HomeController::class, 'index']); 🧩 /
Route::get('/about', [HomeController::class, 'about']); 🧩 /about

Route::group(['prefix' => 'user'], function () {
    Route::get('/profile', [ProfileController::class, 'show']); 🧩 /user/profile
    Route::get('/profile/{profile_id}', [ProfileController::class, 'show']); 🧩 /user/profile/{profile_id}
});
```

```php
// api.php

<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\Api\AuthController;
use App\Http\Controllers\Api\PostController;

Route::post('/login', [AuthController::class, 'login']);
Route::post('/register', [AuthController::class, 'register']);

Route::group(['prefix' => 'v1', 'middleware' => ['auth:sanctum']], function () {
    Route::get('/posts', [PostController::class, 'index']);
    Route::get('/posts/{id}', [PostController::class, 'show']);
    Route::post('/posts', [PostController::class, 'store']);
});
```

The extension will display:

```php
<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\Api\AuthController;
use App\Http\Controllers\Api\PostController;

Route::post('/login', [AuthController::class, 'login']); 🧩 /api/login
Route::post('/register', [AuthController::class, 'register']); 🧩 /api/register

Route::group(['prefix' => 'v1', 'middleware' => ['auth:sanctum']], function () {
    Route::get('/posts', [PostController::class, 'index']); 🧩 /api/v1/posts
    Route::get('/posts/{id}', [PostController::class, 'show']); 🧩 /api/v1/posts/{id}
    Route::post('/posts', [PostController::class, 'store']); 🧩 /api/v1/posts
});
```

## Commands

- `Laravel Routes: Toggle Annotations` - Toggle route annotations on/off

## Keyboard Shortcuts

- **Mac**: `Cmd+Shift+U`
- **Windows/Linux**: `Ctrl+Shift+U`

## Requirements

- VS Code 1.74.0 or higher
- PHP language support (for file detection)

## Limitations

- Currently only supports static route group parsing (no dynamic prefix evaluation)
- Only processes `routes/web.php` | `routes/api.php` files
- Uses regex-based parsing (not a full PHP AST parser)

## Development

To build and test this extension:

1. Clone the repository
2. Run `npm install`
3. Run `npm run compile`
4. Press F5 to launch Extension Development Host
5. Open a Laravel project with `routes/web.php` | `routes/api.php`

## Packaging

Then install with:
```bash
Unzip the directory in your sublime packages directory
```

## License

MIT
