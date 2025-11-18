package com.bank.demo.model;
import java.util.HashMap;
import java.util.Map;

import org.postgresql.util.PGobject;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;

import jakarta.persistence.AttributeConverter;
import jakarta.persistence.Converter;

@Converter(autoApply = true)
public class JsonToMapConverter implements AttributeConverter<Map<String, Object>, Object> {

    private static final ObjectMapper objectMapper = new ObjectMapper();

    @Override
    public Object convertToDatabaseColumn(Map<String, Object> attribute) {
        if (attribute == null || attribute.isEmpty()) return null;

        try {
            PGobject pgObject = new PGobject();
            pgObject.setType("jsonb"); // <--- necessary
            pgObject.setValue(objectMapper.writeValueAsString(attribute));
            return pgObject;
        } catch (Exception e) {
            throw new IllegalArgumentException("Failed to convert Map to JSONB", e);
        }
    }

    @Override
    public Map<String, Object> convertToEntityAttribute(Object dbData) {
        if (dbData == null) return new HashMap<>();

        try {
            String json = dbData instanceof PGobject ? ((PGobject) dbData).getValue() : dbData.toString();
            return objectMapper.readValue(json, new TypeReference<>() {});
        } catch (Exception e) {
            throw new IllegalArgumentException("Failed to convert JSONB to Map", e);
        }
    }
}



