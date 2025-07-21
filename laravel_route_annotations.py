import sublime
import sublime_plugin
import re
import os

class LaravelRouteAnnotationsListener(sublime_plugin.EventListener):

    phantom_sets = {}
    is_enabled = True

    def on_load_async(self, view):
        self.update_decorations_for_view(view)

    def on_modified_async(self, view):
        if not hasattr(self, 'modified_timeout_id'):
            self.modified_timeout_id = None

        if self.modified_timeout_id:
            view.window().cancel_timeout(self.modified_timeout_id)

        self.modified_timeout_id = view.window().set_timeout(
            lambda: self.update_decorations_for_view(view), 500
        )

    def on_activated_async(self, view):
        self.update_decorations_for_view(view)

    def on_close(self, view):
        self.erase_phantoms_for_view(view)
        if view.id() in self.phantom_sets:
            del self.phantom_sets[view.id()]

    def erase_phantoms_for_view(self, view):
        if view.id() in self.phantom_sets:
            for phantom_id in self.phantom_sets[view.id()]:
                view.erase_phantom_by_id(phantom_id)
            self.phantom_sets[view.id()] = []

    def is_laravel_route_file(self, view):
        file_name = view.file_name()
        if not file_name:
            return False
        return file_name and "routes" in file_name and file_name.endswith(".php")

    def get_file_prefixes(self, view):
        file_name = view.file_name()
        global_base_prefix = ""
        file_specific_prefix = ""

        if not file_name:
            return global_base_prefix, file_specific_prefix

        if "routes/api.php" in file_name:
            global_base_prefix = "api"
        elif "routes/api_v1.php" in file_name:
            global_base_prefix = "api"
            file_specific_prefix = "v1"
        elif "routes/web.php" in file_name:
            global_base_prefix = ""
            file_specific_prefix = ""

        return global_base_prefix, file_specific_prefix

    def parse_route_groups(self, content):
        line_prefixes = {}
        lines = content.split('\n')
        group_stack = ['']
        brace_level_stack = [0]
        current_brace_depth = 0

        for i, line in enumerate(lines):
            trimmed_line = line.strip()

            open_braces = line.count('{')
            close_braces = line.count('}')
            current_brace_depth += open_braces - close_braces

            prefix_match = None
            patterns = [
                r"Route::group\s*\(\s*\[\s*['\"]prefix['\"]\s*=>\s*['\"]([^'\"]+)['\"]",
                r"->prefix\s*\(\s*['\"]([^'\"]+)['\"]\s*\)\s*->.*group\s*\(",
                r"Route::\w+\s*\(.*?\)\s*->.*?prefix\s*\(\s*['\"]([^'\"]+)['\"]\s*\).*?->group\s*\(",
                r"Route::controller\s*\(.*?::class\)\s*->prefix\s*\(\s*['\"]([^'\"]+)['\"]\s*\).*?->group\s*\(",
                r"Route::prefix\s*\(\s*['\"]([^'\"]+)['\"]\s*\)\s*->group\s*\("
            ]

            for pattern in patterns:
                match = re.search(pattern, trimmed_line)
                if match:
                    prefix_match = match
                    break

            if prefix_match:
                prefix = prefix_match.group(1)
                current_prefix = group_stack[-1] if group_stack else ''

                if current_prefix:
                    new_prefix = "{}/{}".format(current_prefix, prefix).replace('//', '/')
                else:
                    new_prefix = prefix

                group_stack.append(new_prefix.strip('/'))
                brace_level_stack.append(current_brace_depth)

            while len(brace_level_stack) > 1 and current_brace_depth < brace_level_stack[-1]:
                group_stack.pop()
                brace_level_stack.pop()

            line_prefixes[i] = group_stack[-1] if group_stack else ''

        return line_prefixes

    def parse_routes(self, content, global_base_prefix, file_specific_prefix):
        routes = []
        lines = content.split('\n')
        prefixes_by_line = self.parse_route_groups(content)

        for i, line in enumerate(lines):
            trimmed_line = line.strip()
            route_match = re.search(r"Route::(get|post|put|delete|patch|options|any|apiResource)\s*\(\s*['\"]([^'\"]+)['\"]", trimmed_line, re.IGNORECASE)

            if route_match:
                method = route_match.group(1).upper()
                path = route_match.group(2)
                group_prefix = prefixes_by_line.get(i, '')

                calculated_full_path_segments = []

                if global_base_prefix:
                    calculated_full_path_segments.append(global_base_prefix)
                if file_specific_prefix:
                    calculated_full_path_segments.append(file_specific_prefix)
                if group_prefix:
                    calculated_full_path_segments.append(group_prefix)

                if path not in ['', '/']:
                    calculated_full_path_segments.append(path.strip('/'))

                full_path = "/" + "/".join(segment.strip('/') for segment in calculated_full_path_segments if segment).replace('//', '/')
                if not full_path.startswith('/'):
                    full_path = '/' + full_path
                full_path = full_path.replace('//', '/')

                routes.append({
                    "line": i,
                    "path": path,
                    "method": method if method != 'APIRESOURCE' else "APIRESOURCE (Multiple)",
                    "fullPath": full_path
                })
        return routes

    def update_decorations_for_view(self, view):
        if not self.is_enabled or not self.is_laravel_route_file(view):
            self.erase_phantoms_for_view(view)
            return

        content = view.substr(sublime.Region(0, view.size()))
        global_base_prefix, file_specific_prefix = self.get_file_prefixes(view)

        routes = self.parse_routes(content, global_base_prefix, file_specific_prefix)

        self.erase_phantoms_for_view(view)
        self.phantom_sets.setdefault(view.id(), [])

        for route in routes:
            # Get the full line content to measure its length
            line_region = view.line(view.text_point(route["line"], 0))
            line_content = view.substr(line_region)

            # Calculate the point *after* any trailing characters on the line
            # This is key for ensuring it appears truly at the end.
            point = line_region.end()

            # Create a zero-width region at this end point
            region = sublime.Region(point, point)

            # Using inline style with a direct hex color (e.g., a grayish-green)
            # You might need to adjust the `margin-left` in the style to give it some space.
            phantom_html = '<body id="laravel-route-annotation" style="background-color: transparent; margin: 0; padding: 0;"><p style="color: #8FD800; font-style: italic; font-size: 0.9em; margin: 0 0 0 20px; padding: 0;"> 🧩 {}</p></body>'.format(route["fullPath"])

            phantom_id = view.add_phantom(
                "laravel_route_annotations",
                region,
                phantom_html,
                sublime.LAYOUT_INLINE
            )
            if phantom_id:
                self.phantom_sets[view.id()].append(phantom_id)


class LaravelRoutesToggleCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        LaravelRouteAnnotationsListener.is_enabled = not LaravelRouteAnnotationsListener.is_enabled

        window = self.view.window()
        if window:
            active_view = window.active_view()
            if active_view:
                LaravelRouteAnnotationsListener().update_decorations_for_view(active_view)

        if LaravelRouteAnnotationsListener.is_enabled:
            sublime.status_message("Laravel Route annotations enabled")
        else:
            sublime.status_message("Laravel Route annotations disabled")
