const std = @import("std");
const log = std.log;
const builtin = @import("builtin");

// ===== Configuration =====
const DEFAULT_HOST = "0.0.0.0";
const DEFAULT_PORT: u16 = 8080;

const SERVICE_NAME = "devops-info-service";
const SERVICE_VERSION = "1.0.0";
const SERVICE_DESCRIPTION = "DevOps course info service";
const FRAMEWORK_NAME = "Zig std.http";
const TIMEZONE = "UTC";

// Application start time
var start_timestamp: i64 = 0;

pub fn main() !void {
    // Record start time
    start_timestamp = std.time.timestamp();

    const port = getEnvPort();
    const host = getEnvHost();

    const addr = std.net.Address.parseIp4(host, port) catch |err| {
        log.err("Failed to parse address {s}:{d}: {}", .{ host, port, err });
        return err;
    };

    var server = try std.net.Address.listen(addr, .{ .reuse_address = true });
    defer server.deinit();

    log.info("Server listening on http://{s}:{d}", .{ host, port });

    // Main accept loop
    while (true) {
        const conn = server.accept() catch |err| {
            log.err("Failed to accept connection: {s}", .{@errorName(err)});
            continue;
        };

        handleConnection(conn) catch |err| {
            log.err("Error handling connection: {s}", .{@errorName(err)});
        };
        conn.stream.close();
    }
}

fn getEnvPort() u16 {
    const port_str = std.posix.getenv("PORT") orelse return DEFAULT_PORT;
    return std.fmt.parseInt(u16, port_str, 10) catch DEFAULT_PORT;
}

fn getEnvHost() []const u8 {
    const env = std.posix.getenv("HOST") orelse return DEFAULT_HOST;
    return std.mem.sliceTo(env, 0);
}

fn handleConnection(conn: std.net.Server.Connection) !void {
    var recv_buffer: [4096]u8 = undefined;
    var send_buffer: [4096]u8 = undefined;

    var connection_br = conn.stream.reader(&recv_buffer);
    var connection_bw = conn.stream.writer(&send_buffer);

    var http_server = std.http.Server.init(connection_br.interface(), &connection_bw.interface);

    while (http_server.reader.state == .ready) {
        var request = http_server.receiveHead() catch |err| switch (err) {
            error.HttpConnectionClosing => return,
            else => return err,
        };

        // Route based on path
        const path = request.head.target;

        if (std.mem.eql(u8, path, "/")) {
            try handleRoot(&request);
        } else if (std.mem.eql(u8, path, "/health")) {
            try handleHealth(&request);
        } else {
            try handleNotFound(&request);
        }
    }
}

// ===== Route Handlers =====

fn handleRoot(request: *std.http.Server.Request) !void {
    var buffer: [8192]u8 = undefined;
    var fba = std.heap.FixedBufferAllocator.init(&buffer);
    const allocator = fba.allocator();

    // Get request info
    const user_agent = getUserAgent(request);
    const client_ip = getClientIp(request);
    const method = @tagName(request.head.method);

    // Build JSON response
    const json = try buildMainResponse(allocator, client_ip, user_agent, method);

    try request.respond(json, .{
        .extra_headers = &.{
            .{ .name = "Content-Type", .value = "application/json" },
        },
    });
}

fn handleHealth(request: *std.http.Server.Request) !void {
    var buffer: [1024]u8 = undefined;
    var fba = std.heap.FixedBufferAllocator.init(&buffer);
    const allocator = fba.allocator();

    const json = try buildHealthResponse(allocator);

    try request.respond(json, .{
        .extra_headers = &.{
            .{ .name = "Content-Type", .value = "application/json" },
        },
    });
}

fn handleNotFound(request: *std.http.Server.Request) !void {
    const json =
        \\{"error":"Not Found","message":"Endpoint does not exist"}
    ;

    try request.respond(json, .{
        .status = .not_found,
        .extra_headers = &.{
            .{ .name = "Content-Type", .value = "application/json" },
        },
    });
}

// ===== JSON Response Builders =====

fn buildMainResponse(allocator: std.mem.Allocator, client_ip: []const u8, user_agent: []const u8, method: []const u8) ![]const u8 {
    const uptime = getUptime();
    const timestamp = getTimestamp();
    const hostname = getHostname();
    const cpu_count = getCpuCount();

    return std.fmt.allocPrint(allocator,
        \\{{"service":{{"name":"{s}","version":"{s}","description":"{s}","framework":"{s}"}},"system":{{"hostname":"{s}","platform":"{s}","platform_version":"{s}","architecture":"{s}","cpu_count":{d},"zig_version":"{s}"}},"runtime":{{"uptime_seconds":{d},"uptime_human":"{s}","current_time":"{s}","timezone":"{s}"}},"request":{{"client_ip":"{s}","user_agent":"{s}","method":"{s}","path":"/"}},"endpoints":[{{"path":"/","method":"GET","description":"Service information"}},{{"path":"/health","method":"GET","description":"Health check"}}]}}
    , .{
        SERVICE_NAME,
        SERVICE_VERSION,
        SERVICE_DESCRIPTION,
        FRAMEWORK_NAME,
        hostname,
        getPlatform(),
        getPlatformVersion(),
        getArchitecture(),
        cpu_count,
        getZigVersion(),
        uptime.seconds,
        uptime.human,
        timestamp,
        TIMEZONE,
        client_ip,
        user_agent,
        method,
    });
}

fn buildHealthResponse(allocator: std.mem.Allocator) ![]const u8 {
    const uptime = getUptime();
    const timestamp = getTimestamp();

    return std.fmt.allocPrint(allocator,
        \\{{"status":"healthy","timestamp":"{s}","uptime_seconds":{d}}}
    , .{
        timestamp,
        uptime.seconds,
    });
}

// ===== System Information Helpers =====

var hostname_storage: [std.posix.HOST_NAME_MAX]u8 = undefined;
var hostname_slice: []const u8 = "";
var hostname_initialized: bool = false;

fn getHostname() []const u8 {
    if (!hostname_initialized) {
        const hostname = std.posix.gethostname(&hostname_storage) catch {
            hostname_slice = "unknown";
            hostname_initialized = true;
            return hostname_slice;
        };
        hostname_slice = hostname;
        hostname_initialized = true;
    }
    return hostname_slice;
}

fn getPlatform() []const u8 {
    return @tagName(builtin.os.tag);
}

fn getPlatformVersion() []const u8 {
    // Zig doesn't have direct access to OS version, return a placeholder
    return switch (builtin.os.tag) {
        .macos => "macOS",
        .linux => "Linux",
        .windows => "Windows",
        else => "unknown",
    };
}

fn getArchitecture() []const u8 {
    return @tagName(builtin.cpu.arch);
}

fn getCpuCount() usize {
    return std.Thread.getCpuCount() catch 1;
}

fn getZigVersion() []const u8 {
    return builtin.zig_version_string;
}

// ===== Runtime Information Helpers =====

const Uptime = struct {
    seconds: i64,
    human: []const u8,
};

var uptime_human_buf: [64]u8 = undefined;

fn getUptime() Uptime {
    const now = std.time.timestamp();
    const seconds = now - start_timestamp;

    const hours = @divTrunc(seconds, 3600);
    const minutes = @divTrunc(@mod(seconds, 3600), 60);

    const human = std.fmt.bufPrint(&uptime_human_buf, "{d} hours, {d} minutes", .{ hours, minutes }) catch "unknown";

    return Uptime{
        .seconds = seconds,
        .human = human,
    };
}

var timestamp_buf: [32]u8 = undefined;

fn getTimestamp() []const u8 {
    const now = std.time.timestamp();
    const epoch_seconds = std.time.epoch.EpochSeconds{ .secs = @intCast(now) };
    const day_seconds = epoch_seconds.getDaySeconds();
    const epoch_day = epoch_seconds.getEpochDay();
    const year_day = epoch_day.calculateYearDay();
    const month_day = year_day.calculateMonthDay();

    const formatted = std.fmt.bufPrint(&timestamp_buf, "{d:0>4}-{d:0>2}-{d:0>2}T{d:0>2}:{d:0>2}:{d:0>2}Z", .{
        year_day.year,
        @intFromEnum(month_day.month),
        month_day.day_index + 1,
        day_seconds.getHoursIntoDay(),
        day_seconds.getMinutesIntoHour(),
        day_seconds.getSecondsIntoMinute(),
    }) catch "unknown";

    return formatted;
}

// ===== Request Information Helpers =====

fn getUserAgent(request: *std.http.Server.Request) []const u8 {
    // In Zig 0.15.2, headers are accessed via iterateHeaders
    var iter = request.iterateHeaders();
    while (iter.next()) |header| {
        if (std.ascii.eqlIgnoreCase(header.name, "user-agent")) {
            return header.value;
        }
    }
    return "unknown";
}

fn getClientIp(request: *std.http.Server.Request) []const u8 {
    // Check for X-Forwarded-For header first (for proxied requests)
    var iter = request.iterateHeaders();
    while (iter.next()) |header| {
        if (std.ascii.eqlIgnoreCase(header.name, "x-forwarded-for")) {
            return header.value;
        }
    }
    // Default to localhost (connection IP not directly accessible)
    return "127.0.0.1";
}
