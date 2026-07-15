# Replace the Polling Relay with the Stream Bus

- Status: Superseded

## Context

The original worker design polled the database for pending orders. Increasing delay and database load prompted an evaluation of an event stream.

## Decision

Adopt the Stream Bus and retire the Polling Relay after the compatibility window.

## Later status

A later decision replaced this topology. This record remains to preserve the original context and tradeoffs.
