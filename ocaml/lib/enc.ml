(*   Copyright 2020 Maria A Schett

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
*)
open Core
open Z3util
open Consts
open Instruction
open Params
open Sk_util

let pick_instr params j =
  let t_j = mk_t j in
  let instrs = params.instrs in
  let instr iota = num (Params.instr_to_int params iota) in
  let open Z3Ops in
  conj (List.map instrs ~f:(fun iota -> (instr iota == t_j) ==> (iota.effect params.k j))) &&
  disj (List.map instrs ~f:(fun iota -> (instr iota == t_j)))

let nop_propagate params =
  let t j = mk_t j in
  let t' j = mk_t (j+1) in
  let ns = List.range ~start:`inclusive ~stop:`exclusive 0 (params.n - 1) in
  let nop = find_instr params ~id:"NOP" in
  let nop_to_int = Z3util.num (instr_to_int params nop) in
  let open Z3Ops in
  conj (List.map ns ~f:(fun j -> (t j == nop_to_int) ==> (t' j == nop_to_int)))

let bounds_push_args params =
  let a j = mk_a j in
  let ns = List.range ~start:`inclusive ~stop:`exclusive 0 params.n in
  let open Z3Ops in
  conj (List.map ns ~f:(fun j -> num 0 <= a j && a j < bignum params.max_wsz))

let for_all_vars params =
  let fresh_num i = bignum (Z.add params.max_wsz (Z.of_int i)) in
  let open Z3Ops in
  conj (List.mapi params.ss ~f:(fun i s -> s == fresh_num i))

let force_instrs_in_tgt params =
  let instr iota = num (Params.instr_to_int params iota) in
  let open Z3Ops in
  let force_instr iota = disj (List.init params.n ~f:(fun j -> instr iota == mk_t j)) in
  conj (List.map params.instrs_in_tgt ~f:force_instr)

let enc_block params =
  let source_sk = sk_init params.k 0 params.src_ws in
  let target_sk = sk_init params.k params.n params.tgt_ws in
  let ns = List.range ~start:`inclusive ~stop:`exclusive 0 params.n in
  let open Z3Ops in
  source_sk && target_sk && for_all_vars params &&
  conj (List.map ns ~f:(pick_instr params))
  && nop_propagate params
  && bounds_push_args params
  && force_instrs_in_tgt params

let pick_from params instrs j =
  let enc_to_int iota = num (instr_to_int params iota) in
  let open Z3Ops in
  disj (List.map instrs ~f:(fun iota -> enc_to_int iota == mk_t j))

let enc_weight_at params j =
  List.fold (group_instr_by_gas params)
    ~init:((0, []), [])
    ~f:(fun ((prev_gas, all_prev_instrs), constrs) (curr_gas, instrs)  ->
        let weight = curr_gas - prev_gas in
        let constrs' = (pick_from params all_prev_instrs j, weight) :: constrs in
        let acc = (curr_gas, all_prev_instrs @ instrs) in
        (acc, constrs')
      )
  |> Tuple.T2.get2

let enc_weight params =
  List.init params.n ~f:(fun j -> enc_weight_at params j)
