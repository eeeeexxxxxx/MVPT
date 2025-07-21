use anchor_lang::prelude::*;
use anchor_lang::solana_program::program::invoke_signed;
use anchor_lang::solana_program::instruction::{AccountMeta, Instruction};

// TODO: заменить на реальный id после деплоя
declare_id!("33BQPv9UU9moaQPah9umUad4ovijbF2TVmxcGdSmeSJR");

// MarginFi program id (mainnet)
pub const MARGINFI_PROGRAM_ID: &str = "4Mtd6QeQ8e6hw2yffA9H9n1tFoZT3zh7TBTtJU1vE4hN";

#[program]
pub mod arbitrage_program {
    use super::*;

    pub fn initialize(ctx: Context<Initialize>) -> Result<()> {
        msg!("Greetings from: {:?}", ctx.program_id);
        Ok(())
    }

    pub fn execute_arbitrage(
        ctx: Context<ExecuteArbitrage>,
        params: ArbitrageParams,
    ) -> Result<()> {
        require!(params.amount > 0, CustomError::InvalidAmount);
        require!(params.min_profit > 0, CustomError::InvalidProfit);
        // 2. Вызвать MarginFi Flash Loan (CPI, mock дискриминатор)
        msg!("[CPI] MarginFi Flash Loan: amount={} token_mint={}", params.amount, params.token_mint);
        let marginfi_program = ctx.accounts.marginfi_program.key();
        let accounts = vec![
            AccountMeta::new(*ctx.accounts.marginfi_group.key, false),
            AccountMeta::new(*ctx.accounts.marginfi_account.key, false),
            AccountMeta::new(*ctx.accounts.marginfi_bank.key, false),
            AccountMeta::new(*ctx.accounts.user_token_account.key, false),
            AccountMeta::new(*ctx.accounts.temp_token_account.key, false),
            AccountMeta::new_readonly(ctx.accounts.token_program.key(), false),
            AccountMeta::new_readonly(ctx.accounts.system_program.key(), false),
        ];
        // MOCK: дискриминатор flash_loan (8 байт, заменить на реальный из IDL MarginFi)
        let flash_loan_ix_discriminator: [u8; 8] = [0x12, 0x34, 0x56, 0x78, 0x90, 0xab, 0xcd, 0xef];
        let mut data = vec![];
        data.extend_from_slice(&flash_loan_ix_discriminator);
        data.extend_from_slice(&params.amount.to_le_bytes());
        // receiverData (можно пустой для MVP)
        data.extend_from_slice(&(0u64).to_le_bytes());
        let ix = Instruction {
            program_id: marginfi_program,
            accounts,
            data,
        };
        let _ = invoke_signed(
            &ix,
            &[
                ctx.accounts.marginfi_group.to_account_info(),
                ctx.accounts.marginfi_account.to_account_info(),
                ctx.accounts.marginfi_bank.to_account_info(),
                ctx.accounts.user_token_account.to_account_info(),
                ctx.accounts.temp_token_account.to_account_info(),
                ctx.accounts.token_program.to_account_info(),
                ctx.accounts.system_program.to_account_info(),
            ],
            &[],
        );
        // 3. Выполнить swap на DEX (CPI, mock)
        msg!("[CPI] DEX Swap: buy_pool={} sell_pool={}", params.buy_pool, params.sell_pool);
        // TODO: Здесь будет invoke CPI в DEX (Orca/Raydium)
        // 4. Вернуть Flash Loan (MarginFi)
        msg!("[CPI] MarginFi Repay");
        // TODO: Здесь будет возврат Flash Loan (обычно автоматом, если средства возвращены)
        // 5. Проверить профит (mock)
        msg!("[CHECK] Profit >= min_profit: {}", params.min_profit);
        Ok(())
    }
}

#[derive(Accounts)]
pub struct Initialize {}

#[derive(Accounts)]
pub struct ExecuteArbitrage<'info> {
    #[account(mut)]
    pub user: Signer<'info>,
    /// CHECK: MarginFi group
    #[account(mut)]
    pub marginfi_group: UncheckedAccount<'info>,
    /// CHECK: MarginFi account
    #[account(mut)]
    pub marginfi_account: UncheckedAccount<'info>,
    /// CHECK: MarginFi bank
    #[account(mut)]
    pub marginfi_bank: UncheckedAccount<'info>,
    /// CHECK: DEX buy pool
    #[account(mut)]
    pub buy_pool: UncheckedAccount<'info>,
    /// CHECK: DEX sell pool
    #[account(mut)]
    pub sell_pool: UncheckedAccount<'info>,
    /// CHECK: user's token account
    #[account(mut)]
    pub user_token_account: UncheckedAccount<'info>,
    /// CHECK: temp token account for swaps
    #[account(mut)]
    pub temp_token_account: UncheckedAccount<'info>,
    /// CHECK: MarginFi program
    pub marginfi_program: UncheckedAccount<'info>,
    pub token_program: Program<'info, anchor_spl::token::Token>,
    pub system_program: Program<'info, System>,
    pub rent: Sysvar<'info, Rent>,
    pub associated_token_program: Program<'info, anchor_spl::associated_token::AssociatedToken>,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone)]
pub struct ArbitrageParams {
    pub amount: u64,         // сумма Flash Loan (например, в лямпортах)
    pub min_profit: u64,     // минимальный профит (для защиты)
    pub buy_pool: Pubkey,    // адрес пула для покупки (DEX)
    pub sell_pool: Pubkey,   // адрес пула для продажи (DEX)
    pub token_mint: Pubkey,  // mint токена (например, SOL/USDC)
    // можно добавить путь swap-ов, адреса других аккаунтов и т.д.
}

#[error_code]
pub enum CustomError {
    #[msg("Invalid amount")] 
    InvalidAmount,
    #[msg("Invalid min profit")] 
    InvalidProfit,
}
