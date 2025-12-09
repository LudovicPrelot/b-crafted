// =====================================================
// B-CraftD v3.0 - MongoDB Setup Script
// Date: 4 décembre 2025
// Usage: mongo < mongodb_setup_v3.js
// Ou: mongosh < mongodb_setup_v3.js (MongoDB 5.0+)
// =====================================================

// Connexion à la base de données
db = db.getSiblingDB("bcraftd");

print("🚀 B-CraftD v3.0 - Configuration MongoDB");
print("=========================================\n");

// =====================================================
// COLLECTION 1: audit_logs
// Usage: Logs d'audit complets (CRUD operations)
// TTL: 180 jours (6 mois)
// Volume estimé: 100k-1M documents
// =====================================================

var auditLogsExists = db.getCollectionNames().includes("audit_logs");
if (auditLogsExists == false) {
  print("📝 Création collection: audit_logs");

  db.createCollection("audit_logs", {
    validator: {
      $jsonSchema: {
        bsonType: "object",
        required: ["user_id", "action", "table_name", "timestamp"],
        properties: {
          user_id: {
            bsonType: "int",
            description: "ID de l'utilisateur (référence PostgreSQL users.id)"
          },
          action: {
            bsonType: "string",
            enum: ["INSERT", "UPDATE", "DELETE", "SELECT"],
            description: "Type d'action effectuée"
          },
          table_name: {
            bsonType: "string",
            description: "Nom de la table concernée"
          },
          record_id: {
            bsonType: "int",
            description: "ID de l'enregistrement modifié"
          },
          old_values: {
            bsonType: "object",
            description: "Valeurs avant modification (UPDATE/DELETE)"
          },
          new_values: {
            bsonType: "object",
            description: "Valeurs après modification (INSERT/UPDATE)"
          },
          ip_address: {
            bsonType: "string",
            description: "Adresse IP de l'utilisateur"
          },
          user_agent: {
            bsonType: "string",
            description: "User agent du navigateur"
          },
          timestamp: {
            bsonType: "date",
            description: "Date et heure de l'action"
          }
        }
      }
    }
  });

  // Index pour performance
  db.audit_logs.createIndex({ user_id: 1, timestamp: -1 });
  db.audit_logs.createIndex({ table_name: 1, timestamp: -1 });
  db.audit_logs.createIndex({ action: 1, timestamp: -1 });
  db.audit_logs.createIndex({ record_id: 1, table_name: 1 });

  // TTL Index: Suppression automatique après 180 jours
  db.audit_logs.createIndex({ timestamp: 1 }, { expireAfterSeconds: 15552000 });

  print("✅ audit_logs créée avec 5 indexes + TTL 180 jours\n");
}
else {
    print("📝 Collection audit_logs existante");
}

// =====================================================
// COLLECTION 2: crafting_history
// Usage: Historique complet de tous les crafts
// Pas de TTL (données permanentes pour analytics)
// Volume estimé: 500k-5M documents
// =====================================================

var craftingHistoryExists = db.getCollectionNames().includes("crafting_history");
if (craftingHistoryExists == false) {
  print("📝 Création collection: crafting_history");

  db.createCollection("crafting_history", {
    validator: {
      $jsonSchema: {
        bsonType: "object",
        required: ["user_id", "recipe_id", "crafted_at", "success"],
        properties: {
          user_id: {
            bsonType: "int",
            description: "ID de l'utilisateur"
          },
          recipe_id: {
            bsonType: "int",
            description: "ID de la recette craftée"
          },
          resource_id: {
            bsonType: "int",
            description: "ID de la ressource produite"
          },
          quantity_crafted: {
            bsonType: "int",
            minimum: 1,
            description: "Quantité craftée"
          },
          ingredients_used: {
            bsonType: "array",
            items: {
              bsonType: "object",
              required: ["resource_id", "quantity"],
              properties: {
                resource_id: { bsonType: "int" },
                quantity: { bsonType: "int" }
              }
            },
            description: "Liste des ingrédients utilisés"
          },
          workshop_id: {
            bsonType: ["int", "null"],
            description: "ID de l'atelier utilisé (si applicable)"
          },
          workshop_durability_before: {
            bsonType: ["int", "null"],
            description: "Durabilité de l'atelier avant craft"
          },
          workshop_durability_after: {
            bsonType: ["int", "null"],
            description: "Durabilité de l'atelier après craft"
          },
          profession_id: {
            bsonType: "int",
            description: "ID de la profession utilisée"
          },
          profession_level: {
            bsonType: "int",
            description: "Niveau de la profession au moment du craft"
          },
          experience_gained: {
            bsonType: "int",
            description: "XP de profession gagnée"
          },
          success: {
            bsonType: "bool",
            description: "Craft réussi ou échoué"
          },
          crafting_time_seconds: {
            bsonType: "int",
            description: "Temps de craft en secondes"
          },
          weather_bonus: {
            bsonType: "double",
            description: "Multiplicateur météo appliqué"
          },
          season_bonus: {
            bsonType: "double",
            description: "Multiplicateur saison appliqué"
          },
          mastery_bonus: {
            bsonType: "double",
            description: "Multiplicateur maîtrise appliqué"
          },
          crafted_at: {
            bsonType: "date",
            description: "Date et heure du craft"
          }
        }
      }
    }
  });

  // Index pour analytics
  db.crafting_history.createIndex({ user_id: 1, crafted_at: -1 });
  db.crafting_history.createIndex({ recipe_id: 1, crafted_at: -1 });
  db.crafting_history.createIndex({ resource_id: 1, crafted_at: -1 });
  db.crafting_history.createIndex({ profession_id: 1, crafted_at: -1 });
  db.crafting_history.createIndex({ success: 1, crafted_at: -1 });
  db.crafting_history.createIndex({ crafted_at: -1 }); // Index temporel global

  print("✅ crafting_history créée avec 6 indexes (pas de TTL)\n");
}
else {
    print("📝 Collection crafting_history existante");
}

// =====================================================
// VÉRIFICATION DE LA CONFIGURATION
// =====================================================

print("\n📊 Résumé de la Configuration MongoDB");
print("======================================");

const collections = db.getCollectionNames();
print(`\n✅ Collections créées/existantes: ${collections.length}`);
collections.forEach(col => print(`   - ${col}`));

print("\n📈 Index créés/existants:");
collections.forEach(col => {
  const indexes = db.getCollection(col).getIndexes();
  print(`   ${col}: ${indexes.length} index`);
});

print("\n🔒 Validateurs JSON Schema actifs:");
const collectionsWithValidators = ["audit_logs", "crafting_history"];
print(`   ${collectionsWithValidators.length} collections avec validation`);

print("\n⏰ TTL Index configurés:");
print("   - audit_logs: 180 jours");

print("\n💾 Estimation espace disque (1 an, 10k users):");
print("   - audit_logs: ~5 GB");
print("   - crafting_history: ~10 GB");
print("   TOTAL: ~15 GB");

// =====================================================
// DONNÉES DE TEST (optionnel)
// =====================================================


if (auditLogsExists == false) {
  print("\n🧪 Insertion de données de test audit_logs...");

  // Test audit_logs
  db.audit_logs.insertOne({
    user_id: 1,
    action: "INSERT",
    table_name: "users",
    record_id: 1,
    new_values: { login: "test_user", email: "test@bcraftd.com" },
    ip_address: "127.0.0.1",
    user_agent: "Mozilla/5.0",
    timestamp: new Date()
  });
  print("✅ document de test insérés\n");
}
if (craftingHistoryExists == false) {
  print("\n🧪 Insertion de données de test crafting_history...");

  // Test crafting_history
  db.crafting_history.insertOne({
    user_id: 1,
    recipe_id: 1,
    resource_id: 10,
    quantity_crafted: 5,
    ingredients_used: [
      { resource_id: 1, quantity: 10 },
      { resource_id: 2, quantity: 5 }
    ],
    profession_id: 1,
    profession_level: 25,
    experience_gained: 50,
    success: true,
    crafting_time_seconds: 120,
    weather_bonus: 1.2,
    season_bonus: 1.0,
    mastery_bonus: 1.1,
    crafted_at: new Date()
  });

  print("✅ document de test insérés\n");
}
// =====================================================
// STATISTIQUES FINALES
// =====================================================

print("\n📊 Statistiques des Collections");
print("================================");

collections.forEach(col => {
  const stats = db.getCollection(col).stats();
  print(`\n${col}:`);
  print(`   Documents: ${stats.count}`);
  print(`   Taille: ${(stats.size / 1024).toFixed(2)} KB`);
  print(`   Index: ${stats.nindexes}`);
});

print("\n✅ Configuration MongoDB terminée avec succès !");
print("================================================\n");

print("\n💡 Commandes utiles:");
print("   - Vérifier TTL: db.audit_logs.getIndexes()");
print("   - Stats collection: db.audit_logs.stats()");
print("   - Compter docs: db.audit_logs.countDocuments()");
print("   - Purge manuelle: db.audit_logs.deleteMany({ timestamp: { $lt: new Date('2024-01-01') } })");