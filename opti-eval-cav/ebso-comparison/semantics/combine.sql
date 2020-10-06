SELECT original.'source opcode',
       ebso.'target opcode' AS ebso_target,
       ebso.'gas saved' AS ebso_gas_saved,
       syrup.'target_disasm' AS syrup_target,
       syrup.'saved_gas' AS syrup_gas_saved
FROM 'results_PFT' AS syrup JOIN 'result' AS ebso JOIN 'deduped_4bit_2500' As original
ON ebso.'source bytecode' = syrup.'source bytecode' AND ebso.'source bytecode' = original.'source bytecode'
WHERE ebso.'translation validation' = 'true'
