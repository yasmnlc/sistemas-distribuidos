package com.exemplo;

import jakarta.ejb.Stateless; // Mudado de javax para jakarta

@Stateless
public class HelloService {
    public String sayHello(String name) {
        return "Olá, " + name + "! Bem-vindo à API EJB.";
    }
}