use serde::Serialize;
use std::time::Duration;

#[derive(Debug, Clone, Serialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum CheckStatus {
    Pass,
    Fail,
}

#[derive(Debug, Clone, Serialize, PartialEq, Eq)]
pub struct CheckReport {
    pub name: String,
    pub status: CheckStatus,
    pub elapsed_ms: u128,
    pub message: String,
    pub details: Vec<String>,
}

impl CheckReport {
    pub fn pass(name: &str, elapsed: Duration, message: String) -> Self {
        Self {
            name: name.to_string(),
            status: CheckStatus::Pass,
            elapsed_ms: elapsed.as_millis(),
            message,
            details: Vec::new(),
        }
    }

    pub fn fail(name: &str, elapsed: Duration, message: String, details: Vec<String>) -> Self {
        Self {
            name: name.to_string(),
            status: CheckStatus::Fail,
            elapsed_ms: elapsed.as_millis(),
            message,
            details,
        }
    }

    pub fn is_pass(&self) -> bool {
        self.status == CheckStatus::Pass
    }

    pub fn to_json(&self) -> String {
        serde_json::to_string_pretty(self).expect("CheckReport JSON serialization should not fail")
    }
}
