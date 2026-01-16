package com.exemplo;

import jakarta.ws.rs.ApplicationPath; // Mudado de javax para jakarta
import jakarta.ws.rs.core.Application;

@ApplicationPath("/api")
public class RestApplication extends Application {
}